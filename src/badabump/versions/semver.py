from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Union

from badabump.constants import DEFAULT_SEMVER_SCHEMA as SCHEMA
from badabump.versions.exceptions import VersionParseError
from badabump.versions.formatting import format_version
from badabump.versions.parsing import parse_version

if TYPE_CHECKING:
    from typing_extensions import Self

    from badabump.annotations import DictStrStr
    from badabump.configs import UpdateConfig


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


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SemVer:
    major: int
    minor: int
    patch: int

    schema: str = SCHEMA

    @classmethod
    def from_parsed_dict(
        cls, parsed: DictStrStr, *, schema: Union[str, None] = None
    ) -> Self:
        return cls(
            major=int(parsed["major"]),
            minor=int(parsed["minor"]),
            patch=int(parsed["patch"]),
            schema=schema or SCHEMA,
        )

    @classmethod
    def initial(cls, *, schema: Union[str, None] = None) -> Self:
        return cls(major=1, minor=0, patch=0, schema=schema or SCHEMA)

    @classmethod
    def parse(cls, value: str, *, schema: Union[str, None] = None) -> Self:
        maybe_parsed = parse_version(SCHEMA, SCHEMA_PARTS_PARSING, value)
        if maybe_parsed:
            return cls.from_parsed_dict(maybe_parsed, schema=schema)
        raise VersionParseError(schema or SCHEMA, value)

    def format(self) -> str:  # noqa: A003
        return format_version(
            self.schema, SCHEMA_PARTS_FORMATTING, dataclasses.asdict(self)
        )

    def update(self, config: UpdateConfig) -> Self:
        if config.is_pre_release:
            return self

        if config.is_breaking_change:
            return dataclasses.replace(
                self, major=self.major + 1, minor=0, patch=0
            )

        if config.is_minor_change:
            return dataclasses.replace(
                self, major=self.major, minor=self.minor + 1, patch=0
            )

        return dataclasses.replace(self, patch=self.patch + 1)
