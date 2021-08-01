from pathlib import Path
from typing import Optional, Tuple

import attr
import tomli

from badabump import __app__
from badabump.annotations import DictStrAny, T
from badabump.constants import (
    CHANGELOG_LOWER,
    DEFAULT_CHANGELOG_FILE_INCLUDE_DATE,
    DEFAULT_CHANGELOG_FORMAT_TYPE_FILE,
    DEFAULT_CHANGELOG_FORMAT_TYPE_GIT,
    DEFAULT_CHANGELOG_IGNORE_FOOTER_URLS,
    DEFAULT_PR_BRANCH_FORMAT,
    DEFAULT_PR_TITLE_FORMAT,
    DEFAULT_PROJECT_TYPE,
    DEFAULT_SEMVER_SCHEMA,
    DEFAULT_STRICT_MODE,
    DEFAULT_TAG_FORMAT,
    DEFAULT_TAG_SUBJECT_FORMAT,
    DEFAULT_VERSION_SCHEMA,
    DEFAULT_VERSION_TYPE,
)
from badabump.enums import FormatTypeEnum, ProjectTypeEnum, VersionTypeEnum


@attr.dataclass(frozen=True, slots=True)
class ProjectConfig:
    path: Path = attr.Factory(Path.cwd)

    project_type: ProjectTypeEnum = DEFAULT_PROJECT_TYPE

    version_type: VersionTypeEnum = DEFAULT_VERSION_TYPE
    version_schema: str = DEFAULT_VERSION_SCHEMA
    version_files: Tuple[str, ...] = attr.Factory(tuple)

    tag_format: str = DEFAULT_TAG_FORMAT
    tag_subject_format: str = DEFAULT_TAG_SUBJECT_FORMAT
    pr_branch_format: str = DEFAULT_PR_BRANCH_FORMAT
    pr_title_format: str = DEFAULT_PR_TITLE_FORMAT

    changelog_format_type_file: FormatTypeEnum = (
        DEFAULT_CHANGELOG_FORMAT_TYPE_FILE
    )
    changelog_format_type_git: FormatTypeEnum = (
        DEFAULT_CHANGELOG_FORMAT_TYPE_GIT
    )
    changelog_file_include_date: bool = DEFAULT_CHANGELOG_FILE_INCLUDE_DATE
    changelog_ignore_footer_urls: bool = DEFAULT_CHANGELOG_IGNORE_FOOTER_URLS

    post_bump_hook: Optional[str] = None
    strict_mode: bool = DEFAULT_STRICT_MODE

    def __attrs_post_init__(self) -> None:
        if self.version_type == VersionTypeEnum.semver:
            object.__setattr__(self, "version_schema", DEFAULT_SEMVER_SCHEMA)

    @classmethod
    def from_path(cls, path: Path) -> "ProjectConfig":
        if not path.is_dir() or not path.exists():
            raise ValueError(f"Project path does not exist: {path!r}")

        config_data: DictStrAny = {}

        maybe_loaded = load_project_config_data(path)
        if maybe_loaded:
            config_data = maybe_loaded[1]

        maybe_include_date = config_data.get("changelog_file_include_date")
        maybe_ignore_footer_urls = config_data.get(
            "changelog_ignore_footer_urls"
        )
        maybe_strict_mode = config_data.get("strict")

        return cls(
            path=path,
            project_type=guess_project_type(
                config_data.get("project_type"), path=path
            ),
            version_type=guess_version_type(config_data.get("version_type")),
            version_schema=(
                config_data.get("version_schema") or DEFAULT_VERSION_SCHEMA
            ),
            version_files=tuple(config_data.get("version_files") or ()),
            tag_format=config_data.get("tag_format") or DEFAULT_TAG_FORMAT,
            tag_subject_format=(
                config_data.get("tag_subject_format")
                or DEFAULT_TAG_SUBJECT_FORMAT
            ),
            pr_branch_format=(
                config_data.get("pr_branch_format") or DEFAULT_PR_BRANCH_FORMAT
            ),
            pr_title_format=(
                config_data.get("pr_title_format") or DEFAULT_PR_TITLE_FORMAT
            ),
            changelog_format_type_file=guess_changelog_format_type_file(
                config_data.get("changelog_format_type_file"), path
            ),
            changelog_format_type_git=guess_changelog_format_type_git(
                config_data.get("changelog_format_type_git")
            ),
            changelog_file_include_date=if_defined(
                maybe_include_date, DEFAULT_CHANGELOG_FILE_INCLUDE_DATE
            ),
            changelog_ignore_footer_urls=if_defined(
                maybe_ignore_footer_urls, DEFAULT_CHANGELOG_IGNORE_FOOTER_URLS
            ),
            post_bump_hook=config_data.get("post_bump_hook"),
            strict_mode=if_defined(maybe_strict_mode, DEFAULT_STRICT_MODE),
        )


@attr.dataclass(frozen=True, slots=True)
class UpdateConfig:
    is_breaking_change: bool = False
    is_minor_change: bool = False
    is_micro_change: bool = True
    is_pre_release: bool = False

    def __attrs_post_init__(self) -> None:
        values = sorted(
            [
                self.is_breaking_change,
                self.is_minor_change,
                self.is_micro_change,
            ]
        )
        if values != [False, False, True]:
            raise ValueError(
                "Update config allow to be initialized only with one "
                "breaking, minor, or micro change at a time."
            )


def find_changelog_file(path: Path, pattern: str) -> Optional[Path]:
    for item in path.glob(pattern):
        if item.stem.lower() == CHANGELOG_LOWER:
            return item
    return None


def guess_changelog_format_type_file(
    value: Optional[str], path: Path
) -> FormatTypeEnum:
    if value:
        return FormatTypeEnum[value]

    if find_changelog_file(path, "*.md") is not None:
        return FormatTypeEnum.markdown

    if find_changelog_file(path, "*.rst") is not None:
        return FormatTypeEnum.rst

    return DEFAULT_CHANGELOG_FORMAT_TYPE_FILE


def guess_changelog_format_type_git(value: Optional[str]) -> FormatTypeEnum:
    if value:
        return FormatTypeEnum[value]
    return DEFAULT_CHANGELOG_FORMAT_TYPE_GIT


def guess_project_type(value: Optional[str], path: Path) -> ProjectTypeEnum:
    if value:
        return ProjectTypeEnum[value]

    if (path / "package.json").exists():
        return ProjectTypeEnum.javascript

    return DEFAULT_PROJECT_TYPE


def guess_version_type(value: Optional[str]) -> VersionTypeEnum:
    if value:
        return VersionTypeEnum[value]
    return DEFAULT_VERSION_TYPE


def if_defined(value: Optional[T], default: T) -> T:
    return value if value is not None else default


def load_project_config_data(path: Path) -> Optional[Tuple[Path, DictStrAny]]:
    for item in (f".{__app__}.toml", "pyproject.toml"):
        maybe_config_path = path / item
        if not maybe_config_path.exists():
            continue

        data = tomli.loads(maybe_config_path.read_text())
        return (maybe_config_path, data.get("tool", {}).get(__app__, {}) or {})

    return None
