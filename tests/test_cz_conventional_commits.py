import pytest

from commitizen.cz.conventional_commits.conventional_commits import (
    ConventionalCommitsCz,
    parse_scope,
    parse_subject,
)
from commitizen.cz.exceptions import AnswerRequiredError

valid_scopes = ["", "simple", "dash-separated", "camelCase" "UPPERCASE"]

scopes_transformations = [["with spaces", "with-spaces"], [None, ""]]

valid_subjects = ["this is a normal text", "aword"]

subjects_transformations = [["with dot.", "with dot"]]

invalid_subjects = ["", "   ", ".", "   .", "", None]


def test_parse_scope_valid_values():
    for valid_scope in valid_scopes:
        assert valid_scope == parse_scope(valid_scope)


def test_scopes_transformations():
    for scopes_transformation in scopes_transformations:
        invalid_scope, transformed_scope = scopes_transformation
        assert transformed_scope == parse_scope(invalid_scope)


def test_parse_subject_valid_values():
    for valid_subject in valid_subjects:
        assert valid_subject == parse_subject(valid_subject)


def test_parse_subject_invalid_values():
    for valid_subject in invalid_subjects:
        with pytest.raises(AnswerRequiredError):
            parse_subject(valid_subject)


def test_subject_transformations():
    for subject_transformation in subjects_transformations:
        invalid_subject, transformed_subject = subject_transformation
        assert transformed_subject == parse_subject(invalid_subject)


def test_questions(config):
    conventional_commits = ConventionalCommitsCz(config)
    questions = conventional_commits.questions()
    assert isinstance(questions, list)
    assert isinstance(questions[0], dict)


def test_small_answer(config):
    conventional_commits = ConventionalCommitsCz(config)
    answers = {
        "prefix": "fix",
        "scope": "users",
        "subject": "email pattern corrected",
        "is_breaking_change": False,
        "body": "",
        "footer": "",
    }
    message = conventional_commits.message(answers)
    assert message == "fix(users): email pattern corrected"


def test_long_answer(config):
    conventional_commits = ConventionalCommitsCz(config)
    answers = {
        "prefix": "fix",
        "scope": "users",
        "subject": "email pattern corrected",
        "is_breaking_change": False,
        "body": "complete content",
        "footer": "closes #24",
    }
    message = conventional_commits.message(answers)
    assert (
        message
        == "fix(users): email pattern corrected\n\ncomplete content\n\ncloses #24"  # noqa
    )


def test_breaking_change_in_footer(config):
    conventional_commits = ConventionalCommitsCz(config)
    answers = {
        "prefix": "fix",
        "scope": "users",
        "subject": "email pattern corrected",
        "is_breaking_change": True,
        "body": "complete content",
        "footer": "migrate by renaming user to users",
    }
    message = conventional_commits.message(answers)
    print(message)
    assert (
        message
        == "fix(users): email pattern corrected\n\ncomplete content\n\nBREAKING CHANGE: migrate by renaming user to users"  # noqa
    )


def test_example(config):
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    example = conventional_commits.example()
    assert isinstance(example, str)


def test_schema(config):
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    schema = conventional_commits.schema()
    assert isinstance(schema, str)


def test_info(config):
    """just testing a string is returned. not the content"""
    conventional_commits = ConventionalCommitsCz(config)
    info = conventional_commits.info()
    assert isinstance(info, str)


def test_process_commit(config):
    conventional_commits = ConventionalCommitsCz(config)
    message = conventional_commits.process_commit("test(test_scope): this is test msg")
    assert message == "this is test msg"
