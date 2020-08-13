import contextlib
import os
import sys
import tempfile

import questionary

from commitizen import factory, git, out
from commitizen.config import BaseConfig
from commitizen.cz.exceptions import CzException
from commitizen.exceptions import (
    CommitError,
    CustomError,
    DryRunExit,
    NoAnswersError,
    NoCommitBackupError,
    NotAGitProjectError,
    NothingToCommitError,
)


class WrapStdin:
    def __init__(self):
        fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
        tty = open(fd, "wb+", buffering=0)
        self.tty = tty

    def __getattr__(self, key):
        if key == "encoding":
            return "UTF-8"
        return getattr(self.tty, key)

    def __del__(self):
        self.tty.close()


class Commit:
    """Show prompt for the user to create a guided commit."""

    def __init__(self, config: BaseConfig, arguments: dict):
        if not git.is_git_project():
            raise NotAGitProjectError()

        self.config: BaseConfig = config
        self.cz = factory.commiter_factory(self.config)
        self.arguments = arguments
        self.temp_file: str = os.path.join(tempfile.gettempdir(), "cz.commit.backup")

    def read_backup_message(self) -> str:
        # Check the commit backup file exists
        if not os.path.isfile(self.temp_file):
            raise NoCommitBackupError()

        # Read commit message from backup
        with open(self.temp_file, "r") as f:
            return f.read().strip()

    def prompt_commit_questions(self) -> str:
        # Prompt user for the commit message
        cz = self.cz
        questions = cz.questions()
        try:
            answers = questionary.prompt(questions, style=cz.style)
        except ValueError as err:
            root_err = err.__context__
            if isinstance(root_err, CzException):
                raise CustomError(root_err.__str__())
            raise err

        if not answers:
            raise NoAnswersError()
        return cz.message(answers)

    def __call__(self):
        dry_run: bool = self.arguments.get("dry_run")

        commit_msg_file: str = self.arguments.get("commit_msg_file")
        if commit_msg_file:
            old_stdin = sys.stdin
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdin = WrapStdin()
            sys.stdout = open("/dev/tty", "w")
            sys.stderr = open("/dev/tty", "w")

        if git.is_staging_clean() and not dry_run:
            raise NothingToCommitError("No files added to staging!")

        retry: bool = self.arguments.get("retry")

        if retry:
            m = self.read_backup_message()
        else:
            m = self.prompt_commit_questions()

        out.info(f"\n{m}\n")

        if dry_run:
            raise DryRunExit()

        if commit_msg_file:
            sys.stdin.close()
            sys.stdout.close()
            sys.stderr.close()
            sys.stdin = old_stdin
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            defaultmesaage = ""
            with open(commit_msg_file) as f:
                defaultmesaage = f.read()
            with open(commit_msg_file, "w") as f:
                f.write(m)
                f.write(defaultmesaage)
                out.success("Commit message is successful!")
                return

        c = git.commit(m)

        if c.return_code != 0:
            out.error(c.err)

            # Create commit backup
            with open(self.temp_file, "w") as f:
                f.write(m)

            raise CommitError()

        if "nothing added" in c.out or "no changes added to commit" in c.out:
            out.error(c.out)
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(self.temp_file)
            out.write(c.err)
            out.write(c.out)
            out.success("Commit successful!")
