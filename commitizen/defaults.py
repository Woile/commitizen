from typing import Any, Dict, List

name: str = "cz_conventional_commits"
config_files: List[str] = ["pyproject.toml", ".cz.toml"]

DEFAULT_SETTINGS: Dict[str, Any] = {
    "name": "cz_conventional_commits",
    "version": None,
    "version_files": [],
    "tag_format": None,  # example v$version
    "bump_message": None,  # bumped v$current_version to $new_version
    "changelog_file": "CHANGELOG.md",
}

MAJOR = "MAJOR"
MINOR = "MINOR"
PATCH = "PATCH"

version_parser = r"(?P<version>([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?)"
bump_message = "bump: version $current_version → $new_version"
