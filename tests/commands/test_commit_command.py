import os
import sys

import pytest

from commitizen import cli, cmd, commands
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


@pytest.fixture
def staging_is_clean(mocker):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = False


@pytest.mark.usefixtures("staging_is_clean")
def test_commit(config, mocker):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "", 0)
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {})()
    success_mock.assert_called_once()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_fails_no_backup(config, mocker):
    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "", 0)

    with pytest.raises(NoCommitBackupError) as excinfo:
        commands.Commit(config, {"retry": True})()

    assert NoCommitBackupError.message in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_retry_works(config, mocker):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "closes #21",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("", "error", "", "", 9)
    error_mock = mocker.patch("commitizen.out.error")

    with pytest.raises(CommitError):
        commit_cmd = commands.Commit(config, {})
        temp_file = commit_cmd.temp_file
        commit_cmd()

    prompt_mock.assert_called_once()
    error_mock.assert_called_once()
    assert os.path.isfile(temp_file)

    # Previous commit failed, so retry should pick up the backup commit
    # commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", "", "", 0)
    success_mock = mocker.patch("commitizen.out.success")

    commands.Commit(config, {"retry": True})()

    commit_mock.assert_called_with("feat: user created\n\ncloses #21")
    prompt_mock.assert_called_once()
    success_mock.assert_called_once()
    assert not os.path.isfile(temp_file)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_command_with_dry_run_option(config, mocker):
    prompt_mock = mocker = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "closes #57",
        "footer": "",
    }

    with pytest.raises(DryRunExit):
        commit_cmd = commands.Commit(config, {"dry_run": True})
        commit_cmd()


def test_commit_when_nothing_to_commit(config, mocker):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = True

    with pytest.raises(NothingToCommitError) as excinfo:
        commit_cmd = commands.Commit(config, {})
        commit_cmd()

    assert "No files added to staging!" in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_customized_expected_raised(config, mocker, capsys):
    _err = ValueError()
    _err.__context__ = CzException("This is the root custom err")
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.side_effect = _err

    with pytest.raises(CustomError) as excinfo:
        commit_cmd = commands.Commit(config, {})
        commit_cmd()

    # Assert only the content in the formatted text
    assert "This is the root custom err" in str(excinfo.value)


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_non_customized_expected_raised(config, mocker, capsys):
    _err = ValueError()
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.side_effect = _err

    with pytest.raises(ValueError):
        commit_cmd = commands.Commit(config, {})
        commit_cmd()


@pytest.mark.usefixtures("staging_is_clean")
def test_commit_when_no_user_answer(config, mocker, capsys):
    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = None

    with pytest.raises(NoAnswersError):
        commit_cmd = commands.Commit(config, {})
        commit_cmd()


def test_commit_in_non_git_project(tmpdir, config):
    with tmpdir.as_cwd():
        with pytest.raises(NotAGitProjectError):
            commands.Commit(config, {})


def test_commit_from_pre_commit_msg_hook(config, mocker, capsys):
    testargs = ["cz", "commit", "--commit-msg-file", "some_file"]
    mocker.patch.object(sys, "argv", testargs)

    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "prefix": "feat",
        "subject": "user created",
        "scope": "",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    mocker.patch("commitizen.commands.commit.WrapStdin")
    mocker.patch("os.open")
    reader_mock = mocker.mock_open(read_data="\n\n#test\n")
    mocker.patch("builtins.open", reader_mock, create=True)

    cli.main()

    out, _ = capsys.readouterr()
    assert "Commit message is successful!" in out
    commit_mock.assert_not_called()


def test_WrapStdin(mocker):
    mocker.patch("os.open")
    reader_mock = mocker.mock_open(read_data="data")
    mocker.patch("builtins.open", reader_mock, create=True)

    wrap_stdin = commands.commit.WrapStdin()

    assert wrap_stdin.encoding == "UTF-8"
    assert wrap_stdin.read() == "data"
