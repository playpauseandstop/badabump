import re
from typing import Pattern


VAR_RE = re.compile(r"\{(?P<var>[^\{]+)\}")


def ensure_regexp_dots(value: str) -> str:
    return value.replace(".", r"\.")


def to_regexp(value: str) -> Pattern[str]:
    value = ensure_regexp_dots(value)
    for item in VAR_RE.findall(value):
        value = value.replace(f"{{{item}}}", rf"(?P<{item}>.+)")
    return re.compile(rf"^{value}$")
