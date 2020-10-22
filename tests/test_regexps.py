import re

import pytest

from badabump.regexps import ensure_regexp_dots, to_regexp


@pytest.mark.parametrize(
    "value, expected",
    (
        ("one two three", r"one two three"),
        ("{version}", r"{version}"),
        ("-{type}.{number}", r"-{type}\.{number}"),
        ("{type}{number}", r"{type}{number}"),
    ),
)
def test_ensure_regexp_dots(value, expected):
    assert ensure_regexp_dots(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    (
        ("one two three", re.compile(r"^one two three$")),
        ("{version}", re.compile(r"^(?P<version>.+)$")),
        ("-{type}.{number}", re.compile(r"^-(?P<type>.+)\.(?P<number>.+)$")),
        ("{type}{number}", re.compile(r"^(?P<type>.+)(?P<number>.+)$")),
    ),
)
def test_to_regexp(value, expected):
    assert to_regexp(value) == expected
