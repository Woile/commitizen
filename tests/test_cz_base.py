import pytest

from commitizen.cz.base import BaseCommitizen


class DummyCz(BaseCommitizen):
    def questions(self):
        return [{"type": "input", "name": "commit", "message": "Initial commit:\n"}]

    def message(self, answers):
        return answers["commit"]


def test_base_raises_error(config):
    with pytest.raises(TypeError):
        BaseCommitizen(config)


def test_questions(config):
    cz = DummyCz(config)
    assert isinstance(cz.questions(), list)


def test_message(config):
    cz = DummyCz(config)
    assert cz.message({"commit": "holis"}) == "holis"


def test_example(config):
    cz = DummyCz(config)
    with pytest.raises(NotImplementedError):
        cz.example()


def test_schema(config):
    cz = DummyCz(config)
    with pytest.raises(NotImplementedError):
        cz.schema()


def test_info(config):
    cz = DummyCz(config)
    with pytest.raises(NotImplementedError):
        cz.info()


def test_process_commit(config):
    cz = DummyCz(config)
    message = cz.process_commit("test(test_scope): this is test msg")
    assert message == "test(test_scope): this is test msg"
