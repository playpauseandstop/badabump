from collections.abc import Sequence
from typing import Any, TypeAlias, TypeVar

Argv = Sequence[str]
DictStrAny: TypeAlias = dict[str, Any]
DictStrStr: TypeAlias = dict[str, str]
T = TypeVar("T")
