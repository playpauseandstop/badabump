from __future__ import annotations

import re
from typing import TYPE_CHECKING, Union

from badabump.regexps import ensure_regexp_dots

if TYPE_CHECKING:
    from badabump.annotations import DictStrStr


def build_schema_regexp(schema: str, parts: DictStrStr) -> re.Pattern[str]:
    schema = ensure_regexp_dots(schema)
    for part, regexp in parts.items():
        schema = schema.replace(part, regexp)
    return re.compile(rf"^{schema}$")


def parse_version(
    schema: str, parts: DictStrStr, value: str
) -> Union[DictStrStr, None]:
    maybe_matched = build_schema_regexp(schema, parts).match(value)
    if maybe_matched:
        return maybe_matched.groupdict()
    return None
