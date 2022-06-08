try:
    import tomllib  # type: ignore[import]
except ImportError:
    import tomli

    tomllib = tomli

from typing import cast

from badabump.annotations import DictStrAny


def loads_toml(content: str) -> DictStrAny:
    return cast("DictStrAny", tomllib.loads(content))
