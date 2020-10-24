from badabump.changelog import (
    ChangeLog,
    COMMIT_TYPE_FEATURE,
    ConventionalCommit,
)
from badabump.enums import FormatTypeEnum


CI_BREAKING_COMMIT = "ci!: Use badabump release bot for pushing tags"

DOCS_SCOPE_COMMIT = """docs(openapi): Update descriptions in OpenAPI schema

Issue: #123
"""

FEATURE_COMMIT = """feat: Export necessary types from the package (#31)

- Export types, enums, utils, themes
- Update components to use styled-components ThemeProvider

Issue: IFXND-55
"""


def test_changelog_with_feature_commit():
    changelog = ChangeLog.from_git_commits([FEATURE_COMMIT])
    assert changelog.has_breaking_change is False
    assert changelog.has_minor_change is True
    assert changelog.has_micro_change is False


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
    assert commit.body == "Issue: #123"
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
