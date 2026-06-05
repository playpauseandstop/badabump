from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from badabump.annotations import DictStrAny, DictStrStr


def format_version(schema: str, parts: DictStrStr, context: DictStrAny) -> str:
    for part, template in parts.items():
        schema = schema.replace(part, template)
    return schema.format(**context)
