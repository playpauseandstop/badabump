from typing import Tuple

import pytest

from badabump.configs import UpdateConfig
from badabump.enums import ProjectTypeEnum
from badabump.versions.pre_release import PreRelease, PreReleaseTypeEnum


PRE_RELEASES: Tuple[Tuple[PreRelease, ProjectTypeEnum, str], ...] = (
    (
        PreRelease(pre_release_type=PreReleaseTypeEnum.alpha, number=0),
        ProjectTypeEnum.python,
        "a0",
    ),
    (
        PreRelease(pre_release_type=PreReleaseTypeEnum.alpha, number=0),
        ProjectTypeEnum.javascript,
        "-alpha.0",
    ),
    (
        PreRelease(pre_release_type=PreReleaseTypeEnum.beta, number=1),
        ProjectTypeEnum.python,
        "b1",
    ),
    (
        PreRelease(pre_release_type=PreReleaseTypeEnum.beta, number=1),
        ProjectTypeEnum.javascript,
        "-beta.1",
    ),
    (
        PreRelease(pre_release_type=PreReleaseTypeEnum.rc, number=2),
        ProjectTypeEnum.python,
        "rc2",
    ),
    (
        PreRelease(pre_release_type=PreReleaseTypeEnum.rc, number=2),
        ProjectTypeEnum.javascript,
        "-rc.2",
    ),
)


@pytest.mark.parametrize("pre_release, project_type, expected", PRE_RELEASES)
def test_pre_release_format(
    pre_release: PreRelease, project_type: ProjectTypeEnum, expected: str
):
    assert pre_release.format(project_type=project_type) == expected


@pytest.mark.parametrize("expected, project_type, pre_release", PRE_RELEASES)
def test_pre_release_parse(
    expected: PreRelease, project_type: ProjectTypeEnum, pre_release: str
):
    assert PreRelease.parse(pre_release, project_type=project_type) == expected


@pytest.mark.parametrize(
    "current, update_config, expected",
    (
        # Alpha
        (
            PreRelease(),
            UpdateConfig(is_pre_release=True),
            PreRelease(number=1),
        ),
        (
            PreRelease(),
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(number=1),
        ),
        (
            PreRelease(),
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta),
        ),
        (
            PreRelease(number=1),
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta),
        ),
        # Beta
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta),
            UpdateConfig(is_pre_release=True),
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta, number=1),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta),
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta),
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta, number=1),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta, number=1),
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta, number=1),
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta, number=2),
        ),
        # RC
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc),
            UpdateConfig(is_pre_release=True),
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc, number=1),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc),
            UpdateConfig(
                is_minor_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc, number=1),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc),
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc, number=1),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc, number=1),
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
                is_pre_release=True,
            ),
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc, number=2),
        ),
    ),
)
def test_pre_release_update(
    current: PreRelease, update_config: UpdateConfig, expected: PreRelease
):
    assert current.update(update_config) == expected


@pytest.mark.parametrize(
    "current, update_config",
    (
        (
            PreRelease(),
            UpdateConfig(
                is_breaking_change=True,
                is_micro_change=False,
            ),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.rc),
            UpdateConfig(is_minor_change=True, is_micro_change=False),
        ),
        (
            PreRelease(pre_release_type=PreReleaseTypeEnum.beta),
            UpdateConfig(),
        ),
    ),
)
def test_pre_release_update_not_pre_release(
    current: PreRelease, update_config: UpdateConfig
):
    assert current.update(update_config) is None
