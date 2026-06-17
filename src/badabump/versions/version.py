from __future__ import annotations

import dataclasses
import json
from contextlib import suppress
from typing import cast, TYPE_CHECKING, TypeAlias, Union

from badabump.enums import ProjectTypeEnum, VersionTypeEnum
from badabump.loaders import get_pyproject_toml_metadata, loads_toml
from badabump.regexps import to_regexp
from badabump.versions import calver, pre_release, semver
from badabump.versions.calver import CalVer
from badabump.versions.exceptions import VersionError, VersionParseError
from badabump.versions.parsing import parse_version
from badabump.versions.pre_release import PreRelease
from badabump.versions.semver import SemVer

if TYPE_CHECKING:
    from typing_extensions import Self

    from badabump.annotations import DictStrStr
    from badabump.configs import ProjectConfig, UpdateConfig

    CalOrSemVer: TypeAlias = Union[CalVer, SemVer]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Version:
    version: CalOrSemVer
    pre_release: Union[PreRelease, None] = None

    @classmethod
    def from_tag(cls, value: str, *, config: ProjectConfig) -> Self:
        return cls.parse(
            guess_version_from_tag(value, tag_format=config.tag_format),
            config=config,
        )

    @classmethod
    def guess_initial_version(
        cls, *, config: ProjectConfig, is_pre_release: bool
    ) -> Self:
        maybe_version_str = find_project_version(config)
        if maybe_version_str:
            return cls.parse(
                maybe_version_str, config=config
            ).enforce_pre_release(is_pre_release)

        if config.version_type == VersionTypeEnum.semver:
            return cls(version=SemVer.initial()).enforce_pre_release(
                is_pre_release
            )
        return cls(
            version=CalVer.initial(schema=config.version_schema)
        ).enforce_pre_release(is_pre_release)

    @classmethod
    def parse(cls, value: str, *, config: ProjectConfig) -> Self:
        schema = config.version_schema

        version_cls: type[CalOrSemVer]
        full_schema_parts: DictStrStr
        if config.version_type == VersionTypeEnum.semver:
            version_cls = semver.SemVer
            full_schema_parts = semver.SCHEMA_PARTS_PARSING
        else:
            version_cls = calver.CalVer
            full_schema_parts = calver.SCHEMA_PARTS_PARSING

        with suppress(VersionError):
            return cls(version=version_cls.parse(value, schema=schema))

        full_schema = (
            f"{schema}{pre_release.SCHEMA_MAPPING[config.project_type]}"
        )
        full_schema_parts.update(pre_release.SCHEMA_PARTS_PARSING)

        maybe_parsed = parse_version(full_schema, full_schema_parts, value)
        if maybe_parsed:
            return cls(
                version=version_cls.from_parsed_dict(
                    maybe_parsed, schema=schema
                ),
                pre_release=pre_release.PreRelease.from_parsed_dict(
                    maybe_parsed, project_type=config.project_type
                ),
            )

        raise VersionParseError(schema, value)

    def enforce_pre_release(self, is_pre_release: bool) -> Self:
        if self.pre_release is None and is_pre_release:
            return dataclasses.replace(self, pre_release=PreRelease())
        return self

    def format(self, *, config: ProjectConfig) -> str:  # noqa: A003
        if self.pre_release:
            return (
                f"{self.version.format()}"
                f"{self.pre_release.format(project_type=config.project_type)}"
            )
        return self.version.format()

    def update(self, config: UpdateConfig) -> Self:
        version_class = self.__class__

        if self.pre_release:
            return version_class(
                version=self.version,
                pre_release=self.pre_release.update(config),
            )

        if config.is_pre_release:
            return version_class(
                version=self.version.update(
                    dataclasses.replace(config, is_pre_release=False)
                ),
                pre_release=PreRelease(),
            )

        return version_class(version=self.version.update(config))


def find_project_version(config: ProjectConfig) -> Union[str, None]:
    if config.project_type == ProjectTypeEnum.javascript:
        package_json_path = config.path / "package.json"
        if package_json_path.exists():
            with suppress(KeyError, ValueError):
                return cast(
                    "str", json.loads(package_json_path.read_text())["version"]
                )
    else:
        pyproject_toml_path = config.path / "pyproject.toml"
        if pyproject_toml_path.exists():
            pyproject_toml = loads_toml(pyproject_toml_path.read_text())
            return get_pyproject_toml_metadata(pyproject_toml, "version")

    return None


def guess_version_from_tag(value: str, *, tag_format: str) -> str:
    matched = to_regexp(tag_format).match(value)
    if matched:
        return matched.groupdict()["version"]
    raise ValueError("Tag value does not match given tag format")
