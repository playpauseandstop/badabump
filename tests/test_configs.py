import pytest

from badabump.configs import ProjectConfig, UpdateConfig
from badabump.constants import DEFAULT_SEMVER_SCHEMA
from badabump.enums import VersionTypeEnum


DEFAULT_KWARGS = {
    "is_breaking_change": False,
    "is_minor_change": False,
    "is_micro_change": True,
    "is_pre_release": False,
}


def test_project_config_semver_schema():
    assert (
        ProjectConfig(version_type=VersionTypeEnum.semver).version_schema
        == DEFAULT_SEMVER_SCHEMA
    )


def test_project_config_semver_schema_overwrite():
    assert (
        ProjectConfig(
            version_type=VersionTypeEnum.semver, version_schema="XYZ"
        ).version_schema
        == DEFAULT_SEMVER_SCHEMA
    )


@pytest.mark.parametrize(
    "kwargs",
    (
        {"is_breaking_change": True, "is_micro_change": False},
        {"is_minor_change": True, "is_micro_change": False},
        {"is_pre_release": True},
        {
            "is_breaking_change": True,
            "is_micro_change": False,
            "is_pre_release": True,
        },
        {
            "is_minor_change": True,
            "is_micro_change": False,
            "is_pre_release": True,
        },
    ),
)
def test_update_config(kwargs):
    prepared = {**DEFAULT_KWARGS, **kwargs}
    UpdateConfig(**prepared)


@pytest.mark.parametrize(
    "invalid_kwargs",
    (
        {"is_breaking_change": True},
        {"is_minor_change": True},
        {"is_breaking_change": True, "is_minor_change": True},
        {
            "is_breaking_change": True,
            "is_minor_change": True,
            "is_micro_change": False,
        },
    ),
)
def test_update_config_invalid_kwargs(invalid_kwargs):
    prepared = {**DEFAULT_KWARGS, **invalid_kwargs}
    with pytest.raises(ValueError):
        UpdateConfig(**prepared)
