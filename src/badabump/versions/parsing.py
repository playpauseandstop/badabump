import re
from typing import Optional, Pattern

from badabump.annotations import DictStrStr
from badabump.regexps import ensure_regexp_dots


def build_schema_regexp(schema: str, parts: DictStrStr) -> Pattern[str]:
    schema = ensure_regexp_dots(schema)
    for part, regexp in parts.items():
        schema = schema.replace(part, regexp)
    return re.compile(rf"^{schema}$")


def parse_version(
    schema: str, parts: DictStrStr, value: str
) -> Optional[DictStrStr]:
    maybe_matched = build_schema_regexp(schema, parts).match(value)
    if maybe_matched:
        return maybe_matched.groupdict()
    return None
