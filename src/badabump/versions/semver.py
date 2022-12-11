from typing import Type, TypeVar, Union

import attrs

from badabump.annotations import DictStrStr
from badabump.configs import UpdateConfig
from badabump.constants import DEFAULT_SEMVER_SCHEMA as SCHEMA
from badabump.versions.exceptions import VersionParseError
from badabump.versions.formatting import format_version
from badabump.versions.parsing import parse_version


SCHEMA_PARTS_FORMATTING = {
    "MAJOR": "{major}",
    "MINOR": "{minor}",
    "PATCH": "{patch}",
}
SCHEMA_PARTS_PARSING = {
    "MAJOR": r"(?P<major>\d+)",
    "MINOR": r"(?P<minor>\d+)",
    "PATCH": r"(?P<patch>\d+)",
}


TSemVer = TypeVar("TSemVer", bound="SemVer")


@attrs.frozen(slots=True, kw_only=True)
class SemVer:
    major: int
    minor: int
    patch: int

    schema: str = SCHEMA

    @classmethod
    def from_parsed_dict(
        cls: Type[TSemVer],
        parsed: DictStrStr,
        *,
        schema: Union[str, None] = None,
    ) -> TSemVer:
        return cls(
            major=int(parsed["major"]),
            minor=int(parsed["minor"]),
            patch=int(parsed["patch"]),
            schema=schema or SCHEMA,
        )

    @classmethod
    def initial(
        cls: Type[TSemVer], *, schema: Union[str, None] = None
    ) -> TSemVer:
        return cls(major=1, minor=0, patch=0, schema=schema or SCHEMA)

    @classmethod
    def parse(
        cls: Type[TSemVer], value: str, *, schema: Union[str, None] = None
    ) -> TSemVer:
        maybe_parsed = parse_version(SCHEMA, SCHEMA_PARTS_PARSING, value)
        if maybe_parsed:
            return cls.from_parsed_dict(maybe_parsed, schema=schema)
        raise VersionParseError(schema or SCHEMA, value)

    def format(self) -> str:  # noqa: A003
        return format_version(
            self.schema, SCHEMA_PARTS_FORMATTING, attrs.asdict(self)
        )

    def update(self, config: UpdateConfig) -> "SemVer":
        if config.is_pre_release:
            return self

        if config.is_breaking_change:
            return attrs.evolve(self, major=self.major + 1, minor=0, patch=0)

        if config.is_minor_change:
            return attrs.evolve(
                self, major=self.major, minor=self.minor + 1, patch=0
            )

        return attrs.evolve(self, patch=self.patch + 1)
