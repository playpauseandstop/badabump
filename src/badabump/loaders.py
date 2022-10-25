import sys

from badabump.annotations import DictStrAny


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def loads_toml(content: str) -> DictStrAny:
    return tomllib.loads(content)
