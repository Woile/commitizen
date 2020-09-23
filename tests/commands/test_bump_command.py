import sys

import pytest

from commitizen import cli, cmd, git
from commitizen.exceptions import (
    BumpTagFailedError,
    CurrentVersionNotFoundError,
    DryRunExit,
    ExpectedExit,
    NoCommitsFoundError,
    NoPatternMapError,
    NotAGitProjectError,
    NoVersionSpecifiedError,
)
from tests.utils import create_file_and_commit


@pytest.mark.parametrize(
    "commit_msg",
    (
        "fix: username exception",
        "fix(user): username exception",
        "refactor: remove ini configuration support",
        "refactor(config): remove ini configuration support",
        "perf: update to use multiproess",
        "perf(worker): update to use multiproess",
    ),
)
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_patch_increment(commit_msg, mocker):
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.1.1")
    assert tag_exists is True


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_minor_increment(commit_msg, mocker):
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    cmd_res = cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"')
    assert tag_exists is True and "commit:refs/tags/0.2.0\n" in cmd_res.out


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_minor_increment_annotated(commit_msg, mocker):
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes", "--annotated-tag"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    cmd_res = cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"')
    assert tag_exists is True and "tag:refs/tags/0.2.0\n" in cmd_res.out


@pytest.mark.parametrize("commit_msg", ("feat: new file", "feat(user): new file"))
def test_bump_minor_increment_annotated_config_file(
    commit_msg, mocker, tmp_commitizen_project
):
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_commitizen_cfg_file.write(
        f"{tmp_commitizen_cfg_file.read()}\n" f"annotated_tag = 1"
    )
    create_file_and_commit(commit_msg)
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    cmd_res = cmd.run('git for-each-ref refs/tags --format "%(objecttype):%(refname)"')
    assert tag_exists is True and "tag:refs/tags/0.2.0\n" in cmd_res.out


@pytest.mark.usefixtures("tmp_commitizen_project")
@pytest.mark.parametrize(
    "commit_msg",
    (
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat!: new user interface",
        "feat(user): new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface\n\nBREAKING CHANGE: age is no longer supported",
        "feat(user)!: new user interface",
        "BREAKING CHANGE: age is no longer supported",
        "BREAKING-CHANGE: age is no longer supported",
    ),
)
def test_bump_major_increment(commit_msg, mocker):
    create_file_and_commit(commit_msg)

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("1.0.0")
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_command_prelease(mocker):
    # PRERELEASE
    create_file_and_commit("feat: location")

    testargs = ["cz", "bump", "--prerelease", "alpha", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0a0")
    assert tag_exists is True

    # PRERELEASE BUMP CREATES VERSION WITHOUT PRERELEASE
    testargs = ["cz", "bump"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_on_git_with_hooks_no_verify_disabled(mocker):
    """Bump commit without --no-verify"""
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/pre-commit", "w") as f:
        f.write("#!/usr/bin/env bash\n" 'echo "0.1.0"')
    cmd.run("chmod +x .git/hooks/pre-commit")

    # MINOR
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_tag_exists_raises_exception(mocker):
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/post-commit", "w") as f:
        f.write("#!/usr/bin/env bash\n" "exit 9")
    cmd.run("chmod +x .git/hooks/post-commit")

    # MINOR
    create_file_and_commit("feat: new file")
    git.tag("0.2.0")

    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(BumpTagFailedError) as excinfo:
        cli.main()
    assert "0.2.0" in str(excinfo.value)  # This should be a fatal error


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_on_git_with_hooks_no_verify_enabled(mocker):
    cmd.run("mkdir .git/hooks")
    with open(".git/hooks/pre-commit", "w") as f:
        f.write("#!/usr/bin/env bash\n" 'echo "0.1.0"')
    cmd.run("chmod +x .git/hooks/pre-commit")

    # MINOR
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes", "--no-verify"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True


def test_bump_when_bumpping_is_not_support(mocker, tmp_commitizen_project):
    create_file_and_commit(
        "feat: new user interface\n\nBREAKING CHANGE: age is no longer supported"
    )

    testargs = ["cz", "-n", "cz_jira", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NoPatternMapError) as excinfo:
        cli.main()

    assert "'cz_jira' rule does not support bump" in str(excinfo.value)


@pytest.mark.usefixtures("tmp_git_project")
def test_bump_when_version_is_not_specify(mocker):
    mocker.patch.object(sys, "argv", ["cz", "bump"])

    with pytest.raises(NoVersionSpecifiedError) as excinfo:
        cli.main()

    assert NoVersionSpecifiedError.message in str(excinfo.value)


@pytest.mark.usefixtures("tmp_commitizen_project")
def test_bump_when_no_new_commit(mocker):
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(NoCommitsFoundError) as excinfo:
        cli.main()

    expected_error_message = "[NO_COMMITS_FOUND]\n" "No new commits found."
    assert expected_error_message in str(excinfo.value)


def test_bump_when_version_inconsistent_in_version_files(
    tmp_commitizen_project, mocker
):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("100.999.10000")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_commitizen_cfg_file.write(
        f"{tmp_commitizen_cfg_file.read()}\n"
        f'version_files = ["{str(tmp_version_file)}"]'
    )

    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes", "--check-consistency"]
    mocker.patch.object(sys, "argv", testargs)

    with pytest.raises(CurrentVersionNotFoundError) as excinfo:
        cli.main()

    partial_expected_error_message = "Current version 0.1.0 is not found in"
    assert partial_expected_error_message in str(excinfo.value)


def test_bump_files_only(mocker, tmp_commitizen_project):
    tmp_version_file = tmp_commitizen_project.join("__version__.py")
    tmp_version_file.write("0.1.0")
    tmp_commitizen_cfg_file = tmp_commitizen_project.join("pyproject.toml")
    tmp_commitizen_cfg_file.write(
        f"{tmp_commitizen_cfg_file.read()}\n"
        f'version_files = ["{str(tmp_version_file)}"]'
    )

    create_file_and_commit("feat: new user interface")
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)
    cli.main()
    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is True

    create_file_and_commit("feat: another new feature")
    testargs = ["cz", "bump", "--yes", "--files-only"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(ExpectedExit):
        cli.main()

    tag_exists = git.tag_exist("0.3.0")
    assert tag_exists is False

    with open(tmp_version_file, "r") as f:
        assert "0.3.0" in f.read()


def test_bump_dry_run(mocker, capsys, tmp_commitizen_project):
    create_file_and_commit("feat: new file")

    testargs = ["cz", "bump", "--yes", "--dry-run"]
    mocker.patch.object(sys, "argv", testargs)
    with pytest.raises(DryRunExit):
        cli.main()

    out, _ = capsys.readouterr()
    assert "0.2.0" in out

    tag_exists = git.tag_exist("0.2.0")
    assert tag_exists is False


def test_bump_in_non_git_project(tmpdir, config, mocker):
    testargs = ["cz", "bump", "--yes"]
    mocker.patch.object(sys, "argv", testargs)

    with tmpdir.as_cwd():
        with pytest.raises(NotAGitProjectError):
            with pytest.raises(ExpectedExit):
                cli.main()
