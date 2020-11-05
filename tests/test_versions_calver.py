import datetime

import pytest

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
