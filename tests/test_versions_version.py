import datetime
import json
from pathlib import Path

import attrs
import pytest
import tomli_w

from badabump.configs import ProjectConfig, UpdateConfig
from badabump.enums import ProjectTypeEnum, VersionTypeEnum
from badabump.versions.calver import CalVer, SHORT_YEAR_START
from badabump.versions.exceptions import VersionParseError
from badabump.versions.pre_release import PreRelease, PreReleaseTypeEnum
from badabump.versions.semver import SemVer
from badabump.versions.version import (
    find_project_version,
    guess_version_from_tag,
    Version,
)


SEMVER_PROJECT_CONFIG = ProjectConfig(version_type=VersionTypeEnum.semver)


@pytest.mark.parametrize("version", ("1.0.0", "1.0.0-alpha.2", "1.0.0-rc.0"))
def test_find_project_version_javascript(tmpdir, version):
    tmp_path = Path(tmpdir)
    (tmp_path / "package.json").write_text(json.dumps({"version": version}))

    config = attrs.evolve(
        SEMVER_PROJECT_CONFIG,
        path=tmp_path,
        project_type=ProjectTypeEnum.javascript,
    )
    project_version = find_project_version(config=config)

    assert project_version is not None
    assert project_version == version


@pytest.mark.parametrize("version", ("1.0.0", "1.0.0b2", "1.0.0rc0"))
def test_find_project_version_python(tmpdir, version):
    tmp_path = Path(tmpdir)
    (tmp_path / "pyproject.toml").write_text(
        tomli_w.dumps({"tool": {"poetry": {"version": version}}})
    )

    config = attrs.evolve(
        SEMVER_PROJECT_CONFIG,
        path=tmp_path,
        project_type=ProjectTypeEnum.python,
    )
    project_version = find_project_version(config=config)

    assert project_version is not None
    assert project_version == version


@pytest.mark.parametrize(
    "project_type", (ProjectTypeEnum.javascript, ProjectTypeEnum.python)
)
def test_find_project_version_empty(tmpdir, project_type):
    config = attrs.evolve(SEMVER_PROJECT_CONFIG, path=Path(tmpdir))
    assert find_project_version(config=config) is None


@pytest.mark.parametrize(
    "config, is_pre_release, expected",
    (
        (SEMVER_PROJECT_CONFIG, False, "1.0.0"),
        (SEMVER_PROJECT_CONFIG, True, "1.0.0a0"),
    ),
)
def test_guess_initial_version(tmpdir, config, is_pre_release, expected):
    tmp_config = attrs.evolve(config, path=Path(tmpdir))
    assert (
        Version.guess_initial_version(
            config=tmp_config, is_pre_release=is_pre_release
        ).format(config=config)
        == expected
    )


@pytest.mark.parametrize(
    "value, tag_format, expected",
    (
        ("v1.2.3", "v{version}", "1.2.3"),
        ("v20.1.0a0", "v{version}", "20.1.0a0"),
        ("release/2020.10.20", "release/{version}", "2020.10.20"),
        ("v20.10.20", "{version}", "v20.10.20"),
    ),
)
def test_guess_version_from_tag(value, tag_format, expected):
    assert guess_version_from_tag(value, tag_format=tag_format) == expected


@pytest.mark.parametrize(
    "invalid_value, tag_format",
    (
        ("1.2.3", "v{version}"),
        ("v20.10.20", "release/{version}"),
    ),
)
def test_guess_version_from_tag_invalid_value(invalid_value, tag_format):
    with pytest.raises(ValueError):
        guess_version_from_tag(invalid_value, tag_format=tag_format)


def test_parse_version_parse_error():
    with pytest.raises(VersionParseError):
        Version.parse("invalid", config=SEMVER_PROJECT_CONFIG)


@pytest.mark.parametrize(
    "tag, config, expected",
    (
        (
            "v20.1.0",
            ProjectConfig(),
            Version(version=CalVer(year=2020, minor=1, micro=0)),
        ),
        (
            "v20.1.0b2",
            ProjectConfig(),
            Version(
                version=CalVer(year=2020, minor=1, micro=0),
                pre_release=PreRelease(
                    pre_release_type=PreReleaseTypeEnum.beta, number=2
                ),
            ),
        ),
        (
            "release/20.10.20",
            ProjectConfig(
                tag_format="release/{version}", version_schema="YY.MM.DD"
            ),
            Version(
                version=CalVer(year=2020, month=10, day=20, schema="YY.MM.DD")
            ),
        ),
        (
            "1.2.3-alpha.4",
            ProjectConfig(
                tag_format="{version}",
                project_type=ProjectTypeEnum.javascript,
                version_type=VersionTypeEnum.semver,
            ),
            Version(
                version=SemVer(major=1, minor=2, patch=3),
                pre_release=PreRelease(
                    pre_release_type=PreReleaseTypeEnum.alpha, number=4
                ),
            ),
        ),
    ),
)
def test_version_from_tag(tag, config, expected):
    assert Version.from_tag(tag, config=config) == expected


@pytest.mark.parametrize(
    "current_suffix, update_config, expected_suffix",
    (
        # Micro change
        ("1.0", UpdateConfig(), "1.1"),
        ("1.0", UpdateConfig(is_pre_release=True), "1.1a0"),
        ("1.0a0", UpdateConfig(), "1.0"),
        ("1.0a0", UpdateConfig(is_pre_release=True), "1.0a1"),
        # Minor change
        (
            "1.1",
            UpdateConfig(is_minor_change=True, is_micro_change=False),
            "2.0",
        ),
        (
            "1.1",
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            "2.0a0",
        ),
        (
            "1.1a0",
            UpdateConfig(is_minor_change=True, is_micro_change=False),
            "1.1",
        ),
        (
            "1.1a0",
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            "1.1a1",
        ),
        # Breaking change
        (
            "1.1",
            UpdateConfig(is_breaking_change=True, is_micro_change=False),
            "2.0",
        ),
        (
            "1.1",
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            "2.0a0",
        ),
        (
            "1.1a0",
            UpdateConfig(is_breaking_change=True, is_micro_change=False),
            "1.1",
        ),
        (
            "1.1a0",
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            "1.1b0",
        ),
    ),
)
def test_version_update_calver(current_suffix, update_config, expected_suffix):
    short_year = datetime.datetime.utcnow().year - SHORT_YEAR_START

    current = f"{short_year}.{current_suffix}"
    expected = f"{short_year}.{expected_suffix}"

    current_version = Version.parse(current, config=ProjectConfig())
    next_version = current_version.update(update_config)
    assert next_version.format(config=SEMVER_PROJECT_CONFIG) == expected


@pytest.mark.parametrize(
    "current, update_config, expected",
    (
        # Micro change
        ("1.0.0", UpdateConfig(), "1.0.1"),
        ("1.0.0", UpdateConfig(is_pre_release=True), "1.0.1a0"),
        ("1.0.0a0", UpdateConfig(), "1.0.0"),
        ("1.0.0a0", UpdateConfig(is_pre_release=True), "1.0.0a1"),
        # Minor change
        (
            "1.0.0",
            UpdateConfig(is_minor_change=True, is_micro_change=False),
            "1.1.0",
        ),
        (
            "1.0.0",
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            "1.1.0a0",
        ),
        (
            "1.0.0a0",
            UpdateConfig(is_minor_change=True, is_micro_change=False),
            "1.0.0",
        ),
        (
            "1.0.0a0",
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            "1.0.0a1",
        ),
        # Breaking change
        (
            "1.0.0",
            UpdateConfig(is_breaking_change=True, is_micro_change=False),
            "2.0.0",
        ),
        (
            "1.0.0",
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            "2.0.0a0",
        ),
        (
            "1.0.0a0",
            UpdateConfig(is_breaking_change=True, is_micro_change=False),
            "1.0.0",
        ),
        (
            "1.0.0a0",
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            "1.0.0b0",
        ),
    ),
)
def test_version_update_semver(current, update_config, expected):
    current_version = Version.parse(current, config=SEMVER_PROJECT_CONFIG)
    next_version = current_version.update(update_config)
    assert next_version.format(config=SEMVER_PROJECT_CONFIG) == expected
