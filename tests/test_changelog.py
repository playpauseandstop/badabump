from badabump.changelog import (
    ChangeLog,
    COMMIT_TYPE_FEATURE,
    ConventionalCommit,
)


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


def test_feature_commit():
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
