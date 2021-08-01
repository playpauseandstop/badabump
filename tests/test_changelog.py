import datetime

import pytest

from badabump.changelog import (
    ChangeLog,
    COMMIT_TYPE_FEATURE,
    ConventionalCommit,
    version_header,
)
from badabump.enums import ChangeLogTypeEnum, FormatTypeEnum


CI_BREAKING_COMMIT = "ci!: Use badabump release bot for pushing tags"

DOCS_SCOPE_COMMIT = """docs(openapi): Update descriptions in OpenAPI schema

Ref: #123
"""

FEATURE_COMMIT = """feat: Export necessary types from the package (#31)

- Export types, enums, utils, themes
- Update components to use styled-components ThemeProvider

Issue: IFXND-55
"""

FIX_COMMIT = "fix: Update logic behind math operations"

FIX_COMMIT_WITH_URL = f"""{FIX_COMMIT}

Fixes: https://sentry.io/organizations/organization/issues/123456
"""

INVALID_COMMIT = "something"

REFACTOR_COMMIT = """refactor: Change algorigthm to use

Fixes: DEV-1010
"""

CHANGELOG_EMPTY = "No changes since last pre-release"

CHANGELOG_FILE_MD = """## Features:

- [IFXND-55] Export necessary types from the package (#31)

## Fixes:

- Update logic behind math operations

## Refactoring:

- [DEV-1010] Change algorigthm to use

## Other:

- **BREAKING CHANGE:** Use badabump release bot for pushing tags
- [#123] (**openapi**) Update descriptions in OpenAPI schema"""

CHANGELOG_FILE_MD_PRE = """### Features:

- [IFXND-55] Export necessary types from the package (#31)

### Fixes:

- Update logic behind math operations

### Refactoring:

- [DEV-1010] Change algorigthm to use

### Other:

- **BREAKING CHANGE:** Use badabump release bot for pushing tags
- [#123] (**openapi**) Update descriptions in OpenAPI schema"""

CHANGELOG_FILE_RST = CHANGELOG_GIT_RST = """**Features:**

- [IFXND-55] Export necessary types from the package (#31)

**Fixes:**

- Update logic behind math operations

**Refactoring:**

- [DEV-1010] Change algorigthm to use

**Other:**

- **BREAKING CHANGE:** Use badabump release bot for pushing tags
- [#123] (**openapi**) Update descriptions in OpenAPI schema"""

CHANGELOG_GIT_MD = """Features:
---------

- [IFXND-55] Export necessary types from the package (#31)

Fixes:
------

- Update logic behind math operations

Refactoring:
------------

- [DEV-1010] Change algorigthm to use

Other:
------

- **BREAKING CHANGE:** Use badabump release bot for pushing tags
- [#123] (**openapi**) Update descriptions in OpenAPI schema"""

UTCNOW = datetime.datetime.utcnow()


@pytest.mark.parametrize(
    "changelog_type, format_type, expected",
    (
        (
            ChangeLogTypeEnum.changelog_file,
            FormatTypeEnum.markdown,
            CHANGELOG_EMPTY,
        ),
        (
            ChangeLogTypeEnum.changelog_file,
            FormatTypeEnum.rst,
            CHANGELOG_EMPTY,
        ),
        (
            ChangeLogTypeEnum.git_commit,
            FormatTypeEnum.markdown,
            CHANGELOG_EMPTY,
        ),
        (ChangeLogTypeEnum.git_commit, FormatTypeEnum.rst, CHANGELOG_EMPTY),
    ),
)
def test_changelog_empty(changelog_type, format_type, expected):
    changelog = ChangeLog.from_git_commits([])
    content = changelog.format(changelog_type, format_type)
    assert content == expected


@pytest.mark.parametrize(
    "format_type, is_pre_release, expected",
    (
        (FormatTypeEnum.markdown, False, CHANGELOG_FILE_MD),
        (FormatTypeEnum.markdown, True, CHANGELOG_FILE_MD_PRE),
        (FormatTypeEnum.rst, False, CHANGELOG_FILE_RST),
        (FormatTypeEnum.rst, True, CHANGELOG_FILE_RST),
    ),
)
def test_changelog_format_file(format_type, is_pre_release, expected):
    changelog = ChangeLog.from_git_commits(
        [
            FEATURE_COMMIT,
            FIX_COMMIT,
            CI_BREAKING_COMMIT,
            DOCS_SCOPE_COMMIT,
            REFACTOR_COMMIT,
        ]
    )
    content = changelog.format(
        ChangeLogTypeEnum.changelog_file,
        format_type,
        is_pre_release=is_pre_release,
    )
    assert content == expected


@pytest.mark.parametrize(
    "format_type, is_pre_release, expected",
    (
        (FormatTypeEnum.markdown, False, CHANGELOG_GIT_MD),
        (FormatTypeEnum.markdown, True, CHANGELOG_GIT_MD),
        (FormatTypeEnum.rst, False, CHANGELOG_GIT_RST),
        (FormatTypeEnum.rst, True, CHANGELOG_GIT_RST),
    ),
)
def test_changelog_format_git(format_type, is_pre_release, expected):
    changelog = ChangeLog.from_git_commits(
        [
            FEATURE_COMMIT,
            FIX_COMMIT,
            CI_BREAKING_COMMIT,
            DOCS_SCOPE_COMMIT,
            REFACTOR_COMMIT,
        ]
    )
    content = changelog.format(
        ChangeLogTypeEnum.git_commit,
        format_type,
        is_pre_release=is_pre_release,
    )
    assert content == expected


@pytest.mark.parametrize(
    "ignore_footer_urls, expected",
    (
        (True, ""),
        (
            False,
            "[https://sentry.io/organizations/organization/issues/123456] ",
        ),
    ),
)
def test_changelog_ignore_footer_urls(ignore_footer_urls, expected):
    changelog = ChangeLog.from_git_commits([FIX_COMMIT_WITH_URL])
    content = changelog.format(
        ChangeLogTypeEnum.changelog_file,
        FormatTypeEnum.markdown,
        is_pre_release=False,
        ignore_footer_urls=ignore_footer_urls,
    )
    assert (
        content
        == f"""## Fixes:

- {expected}Update logic behind math operations"""
    )


def test_changelog_invalid_commit():
    with pytest.raises(ValueError):
        ChangeLog.from_git_commits([INVALID_COMMIT])


def test_changelog_with_feature_commit():
    changelog = ChangeLog.from_git_commits([FEATURE_COMMIT])
    assert changelog.has_breaking_change is False
    assert changelog.has_minor_change is True
    assert changelog.has_micro_change is False


def test_changelog_with_fix_commit():
    changelog = ChangeLog.from_git_commits([FIX_COMMIT])
    assert changelog.has_breaking_change is False
    assert changelog.has_minor_change is False
    assert changelog.has_micro_change is True


def test_commit_ci_breaking():
    commit = ConventionalCommit.from_git_commit(CI_BREAKING_COMMIT)
    assert commit.commit_type == "ci"
    assert commit.description == "Use badabump release bot for pushing tags"
    assert commit.is_breaking_change is True
    assert commit.body is None
    assert commit.scope is None
    assert (
        commit.format(FormatTypeEnum.markdown)
        == "**BREAKING CHANGE:** Use badabump release bot for pushing tags"
    )
    assert commit.format(FormatTypeEnum.markdown) == commit.format(
        FormatTypeEnum.rst
    )


def test_commit_docs_scope():
    commit = ConventionalCommit.from_git_commit(DOCS_SCOPE_COMMIT)
    assert commit.commit_type == "docs"
    assert commit.description == "Update descriptions in OpenAPI schema"
    assert commit.is_breaking_change is False
    assert commit.body == "Ref: #123"
    assert commit.scope == "openapi"
    assert (
        commit.format(FormatTypeEnum.markdown)
        == "[#123] (**openapi**) Update descriptions in OpenAPI schema"
    )
    assert commit.format(FormatTypeEnum.markdown) == commit.format(
        FormatTypeEnum.rst
    )


def test_commit_feature():
    commit = ConventionalCommit.from_git_commit(FEATURE_COMMIT)
    assert commit.commit_type == COMMIT_TYPE_FEATURE
    assert (
        commit.description == "Export necessary types from the package (#31)"
    )
    assert commit.is_breaking_change is False
    assert commit.issues == ("IFXND-55",)
    assert (
        commit.body
        == """- Export types, enums, utils, themes
- Update components to use styled-components ThemeProvider

Issue: IFXND-55"""
    )
    assert commit.scope is None
    assert (
        commit.format(FormatTypeEnum.markdown)
        == "[IFXND-55] Export necessary types from the package (#31)"
    )
    assert commit.format(FormatTypeEnum.markdown) == commit.format(
        FormatTypeEnum.rst
    )


def test_commit_refactor():
    commit = ConventionalCommit.from_git_commit(REFACTOR_COMMIT)
    assert commit.commit_type == "refactor"
    assert commit.issues == ("DEV-1010",)


@pytest.mark.parametrize(
    "version, format_type, include_date, is_pre_release, expected",
    (
        (
            "1.0.0",
            FormatTypeEnum.markdown,
            True,
            False,
            f"# 1.0.0 ({UTCNOW.date().isoformat()})",
        ),
        (
            "1.0.0rc0",
            FormatTypeEnum.markdown,
            True,
            True,
            f"## 1.0.0rc0 ({UTCNOW.date().isoformat()})",
        ),
        (
            "1.0.0",
            FormatTypeEnum.markdown,
            False,
            False,
            "# 1.0.0",
        ),
        (
            "1.0.0rc0",
            FormatTypeEnum.markdown,
            False,
            True,
            "## 1.0.0rc0",
        ),
        (
            "1.0.0",
            FormatTypeEnum.rst,
            True,
            False,
            f"1.0.0 ({UTCNOW.date().isoformat()})\n==================",
        ),
        (
            "1.0.0rc0",
            FormatTypeEnum.rst,
            True,
            True,
            f"1.0.0rc0 ({UTCNOW.date().isoformat()})\n-----------------",
        ),
        (
            "1.0.0",
            FormatTypeEnum.rst,
            False,
            False,
            "1.0.0\n======",
        ),
        (
            "1.0.0rc0",
            FormatTypeEnum.rst,
            False,
            True,
            "1.0.0rc0\n--------",
        ),
    ),
)
def test_version_header(
    version, format_type, include_date, is_pre_release, expected
):
    assert version_header(
        version,
        format_type,
        include_date=include_date,
        is_pre_release=is_pre_release,
    )
