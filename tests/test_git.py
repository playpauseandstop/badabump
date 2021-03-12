import subprocess

import pytest


COMMITS = (
    "feat: Initial commit",
    "feat: Add new file",
    "docs: Add README",
    "fix: Update implementation",
    """build: Update to latest Python

BREAKING CHANGE: Project now requires only latest Python to run.
""",
)


def test_empty_repository(create_git_repository):
    git = create_git_repository()
    assert git.retrieve_last_tag_or_none() is None

    with pytest.raises(subprocess.CalledProcessError):
        git.retrieve_last_commit()

    with pytest.raises(subprocess.CalledProcessError):
        git.retrieve_last_tag()

    assert git.retrieve_tag_subject("v1.0.0") == ""
    assert git.retrieve_tag_body("v1.0.0") == ""


def test_list_commits(create_git_repository):
    git = create_git_repository(
        ("1.txt", None, COMMITS[0]), ("2.txt", None, COMMITS[1])
    )

    commit_id = subprocess.check_output(
        ["git", "rev-list", "--max-parents=0", "HEAD"], cwd=git.path
    )
    assert git.list_commits(commit_id.strip().decode("utf-8")) == (COMMITS[1],)


def test_list_commits_empty(create_git_repository):
    git = create_git_repository(("1.txt", None, COMMITS[0]))
    assert git.list_commits("HEAD") == ()


def test_retrieve_last_commit(create_git_repository):
    git = create_git_repository(
        ("1.txt", None, COMMITS[0]),
        ("2.txt", None, COMMITS[1]),
    )
    assert git.retrieve_last_commit() == COMMITS[1]


def test_retrieve_last_tag(create_git_repository):
    git = create_git_repository(
        ("1.txt", None, COMMITS[0]), tag=("v1.0.0", "1.0.0 Release")
    )
    assert git.retrieve_last_tag() == "v1.0.0"


def test_retrieve_last_tag_or_none(create_git_repository):
    git = create_git_repository(
        ("1.txt", None, COMMITS[0]), tag=("v1.0.0", "1.0.0 Release")
    )
    assert git.retrieve_last_tag_or_none() == "v1.0.0"


@pytest.mark.parametrize(
    "message, expected_subject, expected_body",
    (
        ("1.0.0 Release", "1.0.0 Release", ""),
        (
            """1.0.0 Release

Features:
---------

- Initial release
""",
            "1.0.0 Release",
            """Features:
---------

- Initial release""",
        ),
    ),
)
def test_retrieve_tag_details(
    create_git_repository, message, expected_subject, expected_body
):
    git = create_git_repository(
        ("1.txt", None, COMMITS[0]), tag=("v1.0.0", message)
    )
    assert git.retrieve_tag_subject("v1.0.0") == expected_subject
    assert git.retrieve_tag_body("v1.0.0") == expected_body
