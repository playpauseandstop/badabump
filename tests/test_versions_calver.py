import datetime

import pytest
import time_machine

from badabump.configs import UpdateConfig
from badabump.versions.calver import CalVer, SHORT_YEAR_START


UTCNOW = datetime.datetime.utcnow()

YEAR = UTCNOW.year
SHORT_YEAR = YEAR - SHORT_YEAR_START
MONTH = UTCNOW.month
DAY = UTCNOW.day


@pytest.mark.parametrize(
    "schema, expected",
    (
        ("YY.MINOR.MICRO", f"{SHORT_YEAR}.1.0"),
        ("YYYY.MM.DD", f"{YEAR}.{MONTH}.{DAY}"),
        ("YYYY_MICRO", f"{YEAR}_0"),
    ),
)
def test_calver_initial(schema, expected):
    assert CalVer.initial(schema=schema).format() == expected


@pytest.mark.parametrize(
    "schema, version, update_kwargs, expected",
    (
        (
            "YYYY.MINOR.MICRO",
            "2018.1.0",
            {
                "is_breaking_change": True,
                "is_minor_change": False,
                "is_micro_change": False,
                "is_pre_release": False,
            },
            "2021.1.0",
        ),
        (
            "YYYY.MINOR.MICRO",
            "2018.1.0",
            {
                "is_breaking_change": True,
                "is_minor_change": False,
                "is_micro_change": False,
                "is_pre_release": True,
            },
            "2021.1.0",
        ),
        (
            "YY.0M_MINOR.MICRO",
            "18.01_1.0",
            {
                "is_breaking_change": True,
                "is_minor_change": False,
                "is_micro_change": False,
                "is_pre_release": False,
            },
            "21.01_1.0",
        ),
        (
            "YY.0M_MINOR.MICRO",
            "18.01_1.0",
            {
                "is_breaking_change": True,
                "is_minor_change": False,
                "is_micro_change": False,
                "is_pre_release": True,
            },
            "21.01_1.0",
        ),
        (
            "YYYY.MINOR",
            "2019.3",
            {
                "is_breaking_change": False,
                "is_minor_change": True,
                "is_micro_change": False,
                "is_pre_release": False,
            },
            "2021.1",
        ),
        (
            "YYYY.MINOR",
            "2019.3",
            {
                "is_breaking_change": False,
                "is_minor_change": True,
                "is_micro_change": False,
                "is_pre_release": True,
            },
            "2021.1",
        ),
        (
            "YYYY.MM.DD",
            "2019.3.1",
            {
                "is_breaking_change": False,
                "is_minor_change": True,
                "is_micro_change": False,
                "is_pre_release": False,
            },
            "2021.1.11",
        ),
        (
            "YYYY.MM.DD",
            "2019.3.1",
            {
                "is_breaking_change": False,
                "is_minor_change": True,
                "is_micro_change": False,
                "is_pre_release": True,
            },
            "2021.1.11",
        ),
        (
            "YY_MINOR.MICRO",
            "20_6.8",
            {
                "is_breaking_change": False,
                "is_minor_change": False,
                "is_micro_change": True,
                "is_pre_release": False,
            },
            "21_1.0",
        ),
        (
            "YY_MINOR.MICRO",
            "20_6.8",
            {
                "is_breaking_change": False,
                "is_minor_change": False,
                "is_micro_change": True,
                "is_pre_release": True,
            },
            "21_1.0",
        ),
        (
            "YYYY.MINOR.MICRO",
            "2020.6.8",
            {
                "is_breaking_change": False,
                "is_minor_change": False,
                "is_micro_change": True,
                "is_pre_release": False,
            },
            "2021.1.0",
        ),
        (
            "YYYY.MINOR.MICRO",
            "2020.6.8",
            {
                "is_breaking_change": False,
                "is_minor_change": False,
                "is_micro_change": True,
                "is_pre_release": True,
            },
            "2021.1.0",
        ),
    ),
)
def test_calver_update_year_change(schema, version, update_kwargs, expected):
    update_config = UpdateConfig(**update_kwargs)
    current = CalVer.parse(version, schema=schema)

    with time_machine.travel("2021-01-11T00:00:00+00:00"):
        assert current.update(update_config).format() == expected
