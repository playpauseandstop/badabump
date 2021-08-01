import datetime
from typing import Optional

import attr

from badabump.annotations import DictStrAny, DictStrStr
from badabump.configs import UpdateConfig
from badabump.constants import DEFAULT_VERSION_SCHEMA
from badabump.versions.exceptions import VersionError, VersionParseError
from badabump.versions.formatting import format_version
from badabump.versions.parsing import parse_version


DEFAULT_MINOR = 1
DEFAULT_MICRO = 0

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
    def initial(cls, *, schema: str) -> "CalVer":
        utcnow = datetime.datetime.utcnow()
        return cls(
            year=utcnow.year,
            month=utcnow.month,
            week=get_week(utcnow),
            day=utcnow.day,
            minor=DEFAULT_MINOR,
            micro=DEFAULT_MICRO,
            schema=schema,
        )

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

        next_minor: Optional[int] = None
        next_micro: Optional[int] = None

        # If year present - attempt to update it with current year
        next_year: Optional[int] = None
        if self.year is not None:
            next_year = utcnow.year
            # New year - new minor release
            if self.year != next_year:
                next_minor, next_micro = DEFAULT_MINOR, DEFAULT_MICRO

        # If month present - attempt to update it with current month
        next_month: Optional[int] = None
        if self.month is not None:
            next_month = utcnow.month
            # New month - new minor release
            if self.month != next_month:
                next_minor, next_micro = DEFAULT_MINOR, DEFAULT_MICRO

        # If week present for version - update it with current week
        next_week: Optional[int] = None
        if self.week is not None:
            next_week = get_week(utcnow)
            # New week - new minor release
            if self.week != next_week:
                next_minor, next_micro = DEFAULT_MINOR, DEFAULT_MICRO

        # If day present for version - update it with current day
        next_day: Optional[int] = None
        if self.day is not None:
            next_day = utcnow.day
            # New day - new minor release
            if self.day != next_day:
                next_minor, next_micro = DEFAULT_MINOR, DEFAULT_MICRO

        if (
            next_minor is None and next_micro is None
        ) and not config.is_pre_release:
            next_minor, next_micro = self.minor, self.micro

            if next_minor is not None and (
                config.is_breaking_change or config.is_minor_change
            ):
                next_minor += 1
                next_micro = 0 if next_micro is not None else None

            if next_micro is not None and config.is_micro_change:
                next_micro += 1

        return attr.evolve(
            self,
            year=next_year,
            month=next_month,
            week=next_week,
            day=next_day,
            minor=next_minor if next_minor is not None else self.minor,
            micro=next_micro if next_micro is not None else self.micro,
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
