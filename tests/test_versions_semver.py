import pytest

from badabump.configs import UpdateConfig
from badabump.versions.semver import SemVer


VERSIONS = (
    (SemVer(major=0, minor=0, patch=1), "0.0.1"),
    (SemVer(major=0, minor=1, patch=2), "0.1.2"),
    (SemVer(major=1, minor=0, patch=1), "1.0.1"),
    (SemVer(major=20, minor=10, patch=10), "20.10.10"),
)


@pytest.mark.parametrize("semver, expected", VERSIONS)
def test_semver_format(semver: SemVer, expected: str):
    assert semver.format() == expected


@pytest.mark.parametrize("expected, semver", VERSIONS)
def test_semver_parse(expected: SemVer, semver: str):
    assert SemVer.parse(semver) == expected


@pytest.mark.parametrize("invalid_semver", ("1", "1.0", "20201020_10"))
def test_semver_parse_invalid(invalid_semver):
    with pytest.raises(ValueError):
        SemVer.parse(invalid_semver)


@pytest.mark.parametrize(
    "semver, update_config, expected",
    (
        (
            SemVer(major=1, minor=0, patch=0),
            UpdateConfig(),
            SemVer(major=1, minor=0, patch=1),
        ),
        (
            SemVer(major=1, minor=0, patch=0),
            UpdateConfig(is_minor_change=True, is_micro_change=False),
            SemVer(major=1, minor=1, patch=0),
        ),
        (
            SemVer(major=1, minor=0, patch=0),
            UpdateConfig(is_breaking_change=True, is_micro_change=False),
            SemVer(major=2, minor=0, patch=0),
        ),
        (
            SemVer(major=1, minor=0, patch=0),
            UpdateConfig(is_pre_release=True),
            SemVer(major=1, minor=0, patch=0),
        ),
        (
            SemVer(major=1, minor=0, patch=0),
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            SemVer(major=1, minor=0, patch=0),
        ),
        (
            SemVer(major=1, minor=0, patch=0),
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            SemVer(major=1, minor=0, patch=0),
        ),
    ),
)
def test_semver_update(
    semver: SemVer, update_config: UpdateConfig, expected: SemVer
):
    assert semver.update(update_config) == expected
