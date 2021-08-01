import attr

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


@attr.dataclass(frozen=True, slots=True)
class SemVer:
    major: int
    minor: int
    patch: int

    schema: str = SCHEMA

    def format(self) -> str:  # noqa: A003
        return format_version(
            self.schema, SCHEMA_PARTS_FORMATTING, attr.asdict(self)
        )

    @classmethod
    def from_parsed_dict(
        cls, parsed: DictStrStr, *, schema: str = None
    ) -> "SemVer":
        return cls(
            major=int(parsed["major"]),
            minor=int(parsed["minor"]),
            patch=int(parsed["patch"]),
            schema=schema or SCHEMA,
        )

    @classmethod
    def initial(cls, *, schema: str = None) -> "SemVer":
        return cls(major=1, minor=0, patch=0, schema=schema or SCHEMA)

    @classmethod
    def parse(cls, value: str, *, schema: str = None) -> "SemVer":
        maybe_parsed = parse_version(SCHEMA, SCHEMA_PARTS_PARSING, value)
        if maybe_parsed:
            return cls.from_parsed_dict(maybe_parsed, schema=schema)
        raise VersionParseError(schema or SCHEMA, value)

    def update(self, config: UpdateConfig) -> "SemVer":
        if config.is_pre_release:
            return self

        if config.is_breaking_change:
            return attr.evolve(self, major=self.major + 1, minor=0, patch=0)

        if config.is_minor_change:
            return attr.evolve(
                self, major=self.major, minor=self.minor + 1, patch=0
            )

        return attr.evolve(self, patch=self.patch + 1)
