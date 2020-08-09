import pytest

from commitizen import BaseCommitizen, defaults, factory
from commitizen.config import BaseConfig
from commitizen.exceptions import NoCommitizenFoundException


def test_factory():
    config = BaseConfig()
    config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    r = factory.commiter_factory(config)
    assert isinstance(r, BaseCommitizen)


def test_factory_fails():
    config = BaseConfig()
    config.settings.update({"name": "Nothing"})
    with pytest.raises(NoCommitizenFoundException) as excinfo:
        factory.commiter_factory(config)

    assert "The committer has not been found in the system." in str(excinfo)
