from enum import Enum, unique


@unique
class ChangeLogTypeEnum(Enum):
    changelog_file = "changelog_file"
    git_commit = "git_commit"


@unique
class FormatTypeEnum(Enum):
    markdown = "markdown"
    rst = "rst"


@unique
class ProjectTypeEnum(Enum):
    python = "python"
    javascript = "javascript"


@unique
class VersionTypeEnum(Enum):
    calver = "calver"
    semver = "semver"
