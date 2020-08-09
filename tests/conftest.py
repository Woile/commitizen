import pytest

from commitizen import cmd, defaults
from commitizen.config import BaseConfig


@pytest.fixture(scope="function")
def tmp_git_project(tmpdir):
    with tmpdir.as_cwd():
        cmd.run("git init")

        yield tmpdir


@pytest.fixture(scope="function")
def tmp_commitizen_project(tmp_git_project):
    with tmp_git_project.as_cwd():
        tmp_commitizen_cfg_file = tmp_git_project.join("pyproject.toml")
        tmp_commitizen_cfg_file.write("[tool.commitizen]\n" 'version="0.1.0"\n')

        yield tmp_git_project


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    return _config
