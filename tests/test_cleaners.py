import pytest

from badabump.cleaners import clean_body, clean_commit_subject, clean_tag_ref


COMMIT_BODY = """Other:
------

- More debug for release tag workflow
- Update release workflow
"""
COMMIT_BODY_CO_AUTHORIZED = """Other:
------

- More debug for release tag workflow
- Update release workflow

Co-authored-by: playpauseandstop <playpauseandstop@users.noreply.github.com>
"""

COMMIT_SUBJECT = "chore: 20.1.0a2 Release"
COMMIT_SUBJECT_WITH_PR = "chore: 20.1.0a2 Release (#5)"


@pytest.mark.parametrize(
    "body, expected",
    ((COMMIT_BODY, COMMIT_BODY), (COMMIT_BODY_CO_AUTHORIZED, COMMIT_BODY)),
)
def test_clean_body(body, expected):
    assert clean_body(body.splitlines()) == expected


@pytest.mark.parametrize(
    "subject, expected",
    (
        (COMMIT_SUBJECT, COMMIT_SUBJECT),
        (COMMIT_SUBJECT_WITH_PR, COMMIT_SUBJECT),
    ),
)
def test_clean_commit_subject(subject, expected):
    assert clean_commit_subject(subject) == expected


@pytest.mark.parametrize(
    "ref, expected",
    (
        ("v20.1.0", "v20.1.0"),
        ("release/20.1.0", "release/20.1.0"),
        ("refs/tags/v20.1.0", "v20.1.0"),
        ("refs/tags/release/20.1.0a0", "release/20.1.0a0"),
    ),
)
def test_clean_tag_ref(ref, expected):
    assert clean_tag_ref(ref) == expected
