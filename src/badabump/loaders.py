try:
    import tomllib
except ImportError:
    import tomli

    tomllib = tomli  # type: ignore[misc]

from typing import cast

from badabump.annotations import DictStrAny


def loads_toml(content: str) -> DictStrAny:
    return cast("DictStrAny", tomllib.loads(content))
