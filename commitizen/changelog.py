"""Design

## Metadata CHANGELOG.md

1. Identify irrelevant information (possible: changelog title, first paragraph)
2. Identify Unreleased area
3. Identify latest version (to be able to write on top of it)

## Parse git log

1. get commits between versions
2. filter commits with the current cz rules
3. parse commit information
4. yield tree nodes
5. format tree nodes
6. produce full tree
7. generate changelog

Extra:
- [x] Generate full or partial changelog
- [x] Include in tree from file all the extra comments added manually
- [x] Add unreleased value
- [x] hook after message is parsed (add extra information like hyperlinks)
- [x] hook after changelog is generated (api calls)
- [x] add support for change_type maps
"""
import os
import re
from collections import defaultdict
from datetime import date
from typing import Callable, Dict, Iterable, List, Optional

from jinja2 import Environment, PackageLoader

from commitizen import defaults
from commitizen.git import GitCommit, GitTag

CATEGORIES = [
    ("fix", "fix"),
    ("breaking", "BREAKING CHANGES"),
    ("feat", "feat"),
    ("refactor", "refactor"),
    ("perf", "perf"),
    ("test", "test"),
    ("build", "build"),
    ("ci", "ci"),
    ("chore", "chore"),
]


def transform_change_type(change_type: str) -> str:
    # TODO: Use again to parse, for this we have to wait until the maps get
    # defined again.
    _change_type_lower = change_type.lower()
    for match_value, output in CATEGORIES:
        if re.search(match_value, _change_type_lower):
            return output
    else:
        raise ValueError(f"Could not match a change_type with {change_type}")


def get_commit_tag(commit: GitCommit, tags: List[GitTag]) -> Optional[GitTag]:
    return next((tag for tag in tags if tag.rev == commit.rev), None)


def generate_tree_from_commits(
    commits: List[GitCommit],
    tags: List[GitTag],
    commit_parser: str,
    changelog_pattern: str,
    unreleased_version: Optional[str] = None,
    change_type_map: Optional[Dict[str, str]] = None,
    changelog_message_builder_hook: Optional[Callable] = None,
) -> Iterable[Dict]:
    pat = re.compile(changelog_pattern)
    map_pat = re.compile(commit_parser, re.MULTILINE)
    # Check if the latest commit is not tagged
    latest_commit = commits[0]
    current_tag: Optional[GitTag] = get_commit_tag(latest_commit, tags)

    current_tag_name: str = unreleased_version or "Unreleased"
    current_tag_date: str = ""
    if unreleased_version is not None:
        current_tag_date = date.today().isoformat()
    if current_tag is not None and current_tag.name:
        current_tag_name = current_tag.name
        current_tag_date = current_tag.date

    changes: Dict = defaultdict(list)
    used_tags: List = [current_tag]
    for commit in commits:
        commit_tag = get_commit_tag(commit, tags)

        if commit_tag is not None and commit_tag not in used_tags:
            used_tags.append(commit_tag)
            yield {
                "version": current_tag_name,
                "date": current_tag_date,
                "changes": changes,
            }
            # TODO: Check if tag matches the version pattern, otherwie skip it.
            # This in order to prevent tags that are not versions.
            current_tag_name = commit_tag.name
            current_tag_date = commit_tag.date
            changes = defaultdict(list)

        matches = pat.match(commit.message)
        if not matches:
            continue

        message = map_pat.match(commit.message)
        message_body = map_pat.search(commit.body)
        if message:
            parsed_message: Dict = message.groupdict()
            # change_type becomes optional by providing None
            change_type = parsed_message.pop("change_type", None)

            if change_type_map:
                change_type = change_type_map.get(change_type, change_type)
            if changelog_message_builder_hook:
                parsed_message = changelog_message_builder_hook(parsed_message, commit)
            changes[change_type].append(parsed_message)
        if message_body:
            parsed_message_body: Dict = message_body.groupdict()
            change_type = parsed_message_body.pop("change_type", None)
            changes[change_type].append(parsed_message_body)

    yield {"version": current_tag_name, "date": current_tag_date, "changes": changes}


def render_changelog(tree: Iterable) -> str:
    loader = PackageLoader("commitizen", "templates")
    env = Environment(loader=loader, trim_blocks=True)
    jinja_template = env.get_template("keep_a_changelog_template.j2")
    changelog: str = jinja_template.render(tree=tree)
    return changelog


def parse_version_from_markdown(value: str) -> Optional[str]:
    if not value.startswith("#"):
        return None
    m = re.search(defaults.version_parser, value)
    if not m:
        return None
    return m.groupdict().get("version")


def parse_title_type_of_line(value: str) -> Optional[str]:
    md_title_parser = r"^(?P<title>#+)"
    m = re.search(md_title_parser, value)
    if not m:
        return None
    return m.groupdict().get("title")


def get_metadata(filepath: str) -> Dict:
    unreleased_start: Optional[int] = None
    unreleased_end: Optional[int] = None
    unreleased_title: Optional[str] = None
    latest_version: Optional[str] = None
    latest_version_position: Optional[int] = None
    if not os.path.isfile(filepath):
        return {
            "unreleased_start": None,
            "unreleased_end": None,
            "latest_version": None,
            "latest_version_position": None,
        }

    with open(filepath, "r") as changelog_file:
        for index, line in enumerate(changelog_file):
            line = line.strip().lower()

            unreleased: Optional[str] = None
            if "unreleased" in line:
                unreleased = parse_title_type_of_line(line)
            # Try to find beginning and end lines of the unreleased block
            if unreleased:
                unreleased_start = index
                unreleased_title = unreleased
                continue
            elif (
                isinstance(unreleased_title, str)
                and parse_title_type_of_line(line) == unreleased_title
            ):
                unreleased_end = index

            # Try to find the latest release done
            version = parse_version_from_markdown(line)
            if version:
                latest_version = version
                latest_version_position = index
                break  # there's no need for more info
        if unreleased_start is not None and unreleased_end is None:
            unreleased_end = index
    return {
        "unreleased_start": unreleased_start,
        "unreleased_end": unreleased_end,
        "latest_version": latest_version,
        "latest_version_position": latest_version_position,
    }


def incremental_build(new_content: str, lines: List, metadata: Dict) -> List:
    """Takes the original lines and updates with new_content.

    The metadata holds information enough to remove the old unreleased and
    where to place the new content

    Args:
        lines: The lines from the changelog
        new_content: This should be placed somewhere in the lines
        metadata: Information about the changelog

    Returns:
        Updated lines
    """
    unreleased_start = metadata.get("unreleased_start")
    unreleased_end = metadata.get("unreleased_end")
    latest_version_position = metadata.get("latest_version_position")
    skip = False
    output_lines: List = []
    for index, line in enumerate(lines):
        if index == unreleased_start:
            skip = True
        elif index == unreleased_end:
            skip = False
            if (
                latest_version_position is None
                or isinstance(latest_version_position, int)
                and isinstance(unreleased_end, int)
                and latest_version_position > unreleased_end
            ):
                continue

        if skip:
            continue

        if (
            isinstance(latest_version_position, int)
            and index == latest_version_position
        ):

            output_lines.append(new_content)
            output_lines.append("\n")

        output_lines.append(line)
    if not isinstance(latest_version_position, int):
        output_lines.append(new_content)
    return output_lines
