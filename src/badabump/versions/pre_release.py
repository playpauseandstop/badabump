from contextlib import suppress
from enum import Enum, unique
from typing import DefaultDict, Optional

import attr

from badabump.annotations import DictStrAny, DictStrStr
from badabump.configs import UpdateConfig
from badabump.enums import ProjectTypeEnum
from badabump.versions.formatting import format_version
from badabump.versions.parsing import parse_version


SCHEMA_MAPPING: DefaultDict[ProjectTypeEnum, str] = DefaultDict(
    lambda: "-TYPE.NUMBER"
)
SCHEMA_MAPPING[ProjectTypeEnum.python] = "TYPENUMBER"

SCHEMA_PARTS_FORMATTING = {
    "TYPE": "{type}",
    "NUMBER": "{number}",
}
SCHEMA_PARTS_PARSING = {
    "TYPE": r"(?P<type>\D+)",
    "NUMBER": r"(?P<number>\d+)",
}


@unique
class PreReleaseTypeEnum(Enum):
    alpha = "alpha"
    beta = "beta"
    rc = "rc"


NEXT_PRE_RELEASE_TYPE = {
    PreReleaseTypeEnum.alpha: PreReleaseTypeEnum.beta,
    PreReleaseTypeEnum.beta: PreReleaseTypeEnum.rc,
    PreReleaseTypeEnum.rc: PreReleaseTypeEnum.rc,
}

PRE_RELEASE_TYPE_MAPPING = {
    ProjectTypeEnum.python: {
        PreReleaseTypeEnum.alpha: "a",
        PreReleaseTypeEnum.beta: "b",
        PreReleaseTypeEnum.rc: "rc",
    },
}


@attr.dataclass(frozen=True, slots=True)
class PreRelease:
    pre_release_type: PreReleaseTypeEnum = PreReleaseTypeEnum.alpha
    number: int = 0

    def format(self, *, project_type: ProjectTypeEnum) -> str:  # noqa: A003
        schema = SCHEMA_MAPPING[project_type]

        context: DictStrAny = {"number": self.number}
        maybe_type_mapping = PRE_RELEASE_TYPE_MAPPING.get(project_type)
        if maybe_type_mapping:
            context["type"] = maybe_type_mapping[self.pre_release_type]
        else:
            context["type"] = self.pre_release_type.value

        return format_version(schema, SCHEMA_PARTS_FORMATTING, context)

    @classmethod
    def from_parsed_dict(
        cls, parsed_dict: DictStrStr, *, project_type: ProjectTypeEnum
    ) -> "PreRelease":
        return cls(
            pre_release_type=guess_pre_release_type(
                parsed_dict["type"], project_type=project_type
            ),
            number=int(parsed_dict["number"]),
        )

    @classmethod
    def parse(
        cls, value: str, *, project_type: ProjectTypeEnum
    ) -> "PreRelease":
        schema = SCHEMA_MAPPING[project_type]

        maybe_parsed = parse_version(schema, SCHEMA_PARTS_PARSING, value)
        if maybe_parsed:
            with suppress(KeyError):
                return cls.from_parsed_dict(
                    maybe_parsed, project_type=project_type
                )

        raise ValueError(
            "Invalid pre-release value, which do not match any supported "
            "project type"
        )

    def update(self, config: UpdateConfig) -> Optional["PreRelease"]:
        if config.is_pre_release is False:
            return None

        if config.is_breaking_change:
            next_type = NEXT_PRE_RELEASE_TYPE[self.pre_release_type]
            if next_type != self.pre_release_type:
                return PreRelease(pre_release_type=next_type, number=0)
            return PreRelease(
                pre_release_type=next_type, number=self.number + 1
            )

        return PreRelease(
            pre_release_type=self.pre_release_type, number=self.number + 1
        )


def guess_pre_release_type(
    value: str, *, project_type: ProjectTypeEnum
) -> PreReleaseTypeEnum:
    maybe_type_mapping = PRE_RELEASE_TYPE_MAPPING.get(project_type)
    if maybe_type_mapping:
        return {
            item: pre_release_type
            for pre_release_type, item in maybe_type_mapping.items()
        }[value]
    return PreReleaseTypeEnum[value]
