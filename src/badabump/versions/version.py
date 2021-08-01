import json
from contextlib import suppress
from typing import cast, Optional, Type, Union

import attr
import tomli

from badabump.annotations import DictStrStr
from badabump.configs import ProjectConfig, UpdateConfig
from badabump.enums import ProjectTypeEnum, VersionTypeEnum
from badabump.regexps import to_regexp
from badabump.versions import calver, pre_release, semver
from badabump.versions.calver import CalVer
from badabump.versions.exceptions import VersionError, VersionParseError
from badabump.versions.parsing import parse_version
from badabump.versions.pre_release import PreRelease
from badabump.versions.semver import SemVer


CalOrSemVer = Union[CalVer, SemVer]


@attr.dataclass(frozen=True, slots=True)
class Version:
    version: CalOrSemVer
    pre_release: Optional[PreRelease] = None

    @classmethod
    def from_tag(cls, value: str, *, config: ProjectConfig) -> "Version":
        return cls.parse(
            guess_version_from_tag(value, tag_format=config.tag_format),
            config=config,
        )

    def format(self, *, config: ProjectConfig) -> str:  # noqa: A003
        if self.pre_release:
            return (
                f"{self.version.format()}"
                f"{self.pre_release.format(project_type=config.project_type)}"
            )
        return self.version.format()

    @classmethod
    def guess_initial_version(
        cls, *, config: ProjectConfig, is_pre_release: bool
    ) -> "Version":
        version = guess_initial_version(config)
        if version.pre_release is None and is_pre_release:
            return attr.evolve(version, pre_release=PreRelease())
        return version

    @classmethod
    def parse(cls, value: str, *, config: ProjectConfig) -> "Version":
        schema = config.version_schema

        version_cls: Type[CalOrSemVer]
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

    def update(self, config: UpdateConfig) -> "Version":
        if self.pre_release:
            return Version(
                version=self.version,
                pre_release=self.pre_release.update(config),
            )

        if config.is_pre_release:
            return Version(
                version=self.version.update(
                    attr.evolve(config, is_pre_release=False)
                ),
                pre_release=PreRelease(),
            )

        return Version(version=self.version.update(config))


def find_project_version(config: ProjectConfig) -> Optional[str]:
    if config.project_type == ProjectTypeEnum.javascript:
        package_json_path = config.path / "package.json"
        if package_json_path.exists():
            try:
                return cast(
                    str, json.loads(package_json_path.read_text())["version"]
                )
            except (KeyError, ValueError):
                ...
    else:
        pyproject_toml_path = config.path / "pyproject.toml"
        if pyproject_toml_path.exists():
            try:
                return cast(
                    str,
                    tomli.loads(pyproject_toml_path.read_text())["tool"][
                        "poetry"
                    ]["version"],
                )
            except (KeyError, ValueError):
                ...

    return None


def guess_initial_version(config: ProjectConfig) -> Version:
    maybe_version_str = find_project_version(config)
    if maybe_version_str:
        return Version.parse(maybe_version_str, config=config)

    if config.version_type == VersionTypeEnum.semver:
        return Version(version=SemVer.initial())
    return Version(version=CalVer.initial(schema=config.version_schema))


def guess_version_from_tag(value: str, *, tag_format: str) -> str:
    matched = to_regexp(tag_format).match(value)
    if matched:
        return matched.groupdict()["version"]
    raise ValueError("Tag value does not match given tag format")
