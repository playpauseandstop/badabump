import datetime
from typing import Optional

import attr

from .exceptions import VersionError, VersionParseError
from .formatting import format_version
from .parsing import parse_version
from ..annotations import DictStrAny, DictStrStr
from ..configs import UpdateConfig
from ..constants import DEFAULT_VERSION_SCHEMA


SHORT_YEAR_START = 2000

SCHEMA_PARTS_FORMATTING = {
    "YYYY": "{year}",
    "YY": "{short_year}",
    "0Y": "{short_year:02d}",
    "MM": "{month}",
    "0M": "{month:02d}",
    "WW": "{week}",
    "0W": "{week:02d}",
    "DD": "{day}",
    "0D": "{day:02d}",
    "MINOR": "{minor}",
    "MICRO": "{micro}",
}
SCHEMA_PARTS_PARSING = {
    "YYYY": r"(?P<year>\d{4})",
    "YY": r"(?P<short_year>\d{2})",
    "0Y": r"(?P<short_year>\d{2})",
    "MM": r"(?P<month>\d{1,2})",
    "0M": r"(?P<month>\d{2})",
    "WW": r"(?P<week>\d{1,2})",
    "0W": r"(?P<week>\d{2})",
    "DD": r"(?P<day>\d{1,2})",
    "0D": r"(?P<day>\d{2})",
    "MINOR": r"(?P<minor>\d+)",
    "MICRO": r"(?P<micro>\d+)",
}


@attr.dataclass(frozen=True, slots=True)
class CalVer:
    year: int
    month: Optional[int] = None
    week: Optional[int] = None
    day: Optional[int] = None
    minor: Optional[int] = None
    micro: Optional[int] = None

    schema: str = DEFAULT_VERSION_SCHEMA

    def format(self) -> str:  # noqa: A003
        return format_version(
            self.schema, SCHEMA_PARTS_FORMATTING, self.get_format_context()
        )

    @classmethod
    def from_parsed_dict(cls, parsed: DictStrStr, *, schema: str) -> "CalVer":
        maybe_year = guess_year(parsed.get("year"), parsed.get("short_year"))
        if maybe_year is None:
            raise VersionError("CalVer version should contains at least year")

        return cls(
            year=maybe_year,
            month=int_or_none(parsed.get("month")),
            week=int_or_none(parsed.get("week")),
            day=int_or_none(parsed.get("day")),
            minor=int_or_none(parsed.get("minor")),
            micro=int_or_none(parsed.get("micro")),
            schema=schema,
        )

    def get_format_context(self) -> DictStrAny:
        return {**attr.asdict(self), "short_year": self.short_year}

    @classmethod
    def parse(cls, value: str, *, schema: str) -> "CalVer":
        maybe_parsed = parse_version(schema, SCHEMA_PARTS_PARSING, value)
        if maybe_parsed:
            return cls.from_parsed_dict(maybe_parsed, schema=schema)
        raise VersionParseError(schema, value)

    @property
    def short_year(self) -> Optional[int]:
        if self.year is None:
            return None
        if self.year < SHORT_YEAR_START:
            return None
        return self.year - SHORT_YEAR_START

    def update(self, config: UpdateConfig) -> "CalVer":
        utcnow = datetime.datetime.utcnow()

        next_minor = self.minor
        next_micro = self.micro

        if not config.is_pre_release:
            if next_minor is not None and (
                config.is_breaking_change or config.is_minor_change
            ):
                next_minor += 1
                next_micro = 0 if next_micro is not None else None

            if next_micro is not None and config.is_micro_change:
                next_micro += 1

        return attr.evolve(
            self,
            year=utcnow.year if self.year else None,
            month=utcnow.month if self.month else None,
            week=get_week(utcnow) if self.week else None,
            day=utcnow.day if self.day else None,
            minor=next_minor,
            micro=next_micro,
        )


def get_week(value: datetime.datetime) -> int:
    return value.isocalendar()[1]


def guess_year(
    year: Optional[str], short_year: Optional[str]
) -> Optional[int]:
    if year is not None:
        return int(year)
    if short_year is not None:
        return SHORT_YEAR_START + int(short_year)
    return None


def int_or_none(value: Optional[str]) -> Optional[int]:
    if value is not None:
        return int(value)
    return None
