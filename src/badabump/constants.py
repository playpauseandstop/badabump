from . import __app__
from .enums import FormatTypeEnum, ProjectTypeEnum, VersionTypeEnum


CHANGELOG_UPPER = "CHANGELOG"
CHANGELOG_LOWER = CHANGELOG_UPPER.lower()

DEFAULT_CHANGELOG_FILE_INCLUDE_DATE = True
DEFAULT_CHANGELOG_FORMAT_TYPE_FILE = FormatTypeEnum.markdown
DEFAULT_CHANGELOG_FORMAT_TYPE_GIT = FormatTypeEnum.markdown
DEFAULT_PROJECT_TYPE = ProjectTypeEnum.python
DEFAULT_TAG_FORMAT = "v{version}"
DEFAULT_VERSION_TYPE = VersionTypeEnum.calver

DEFAULT_CALVER_SCHEMA = DEFAULT_VERSION_SCHEMA = "YY.MINOR.MICRO"
DEFAULT_SEMVER_SCHEMA = "MAJOR.MINOR.PATCH"

FILE_CONFIG_TOML = f".{__app__}.toml"
FILE_PACKAGE_JSON = "package.json"
FILE_PACKAGE_LOCK_JSON = "package-lock.json"
FILE_PYPROJECT_TOML = "pyproject.toml"
FILE_YARN_LOCK = "yarn.lock"
