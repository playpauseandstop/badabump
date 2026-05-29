import sys
from contextlib import suppress
from typing import cast, Union

from badabump.annotations import DictStrAny

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_pyproject_toml_metadata(
    pyproject_toml: DictStrAny, key: str
) -> Union[str, None]:
    if "project" in pyproject_toml:
        with suppress(KeyError, ValueError):
            return cast("str", pyproject_toml["project"][key])

    try:
        return cast("str", pyproject_toml["tool"]["poetry"][key])
    except (KeyError, ValueError):
        return None


def loads_toml(content: str) -> DictStrAny:
    return tomllib.loads(content)
