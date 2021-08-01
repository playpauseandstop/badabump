import subprocess
from pathlib import Path
from typing import Optional, Set, Tuple

import tomli

from badabump.changelog import ChangeLog, in_development_header, version_header
from badabump.cli.output import diff, echo_message
from badabump.configs import find_changelog_file, ProjectConfig
from badabump.constants import (
    CHANGELOG_UPPER,
    FILE_PACKAGE_JSON,
    FILE_PACKAGE_LOCK_JSON,
    FILE_PYPROJECT_TOML,
    FILE_YARN_LOCK,
)
from badabump.enums import ChangeLogTypeEnum, FormatTypeEnum, ProjectTypeEnum
from badabump.exceptions import ConfigError
from badabump.versions import Version


def find_changelog_path(config: ProjectConfig) -> Path:
    path = config.path

    if config.changelog_format_type_file == FormatTypeEnum.markdown:
        default_file = f"{CHANGELOG_UPPER}.md"
        maybe_changelog_path = find_changelog_file(path, "*.md")
    else:
        default_file = f"{CHANGELOG_UPPER}.rst"
        maybe_changelog_path = find_changelog_file(path, "*.rst")

    if maybe_changelog_path:
        return maybe_changelog_path

    return path / default_file


def format_version_str(item: Path, version_str: str) -> str:
    if item.name == "pyproject.toml":
        return f'version = "{version_str}"'

    if item.name == "package.json":
        return f'"version": "{version_str}"'

    return version_str


def guess_version_files(config: ProjectConfig) -> Tuple[str, ...]:
    if config.project_type == ProjectTypeEnum.javascript:
        return (FILE_PACKAGE_JSON,)

    path = config.path
    version_files = []

    maybe_pyproject_toml_path = path / FILE_PYPROJECT_TOML
    if maybe_pyproject_toml_path.exists():
        version_files.append(FILE_PYPROJECT_TOML)

        project_name = (
            tomli.loads(maybe_pyproject_toml_path.read_text())
            .get("tool", {})
            .get("poetry", {})
            .get("name")
        )

        if project_name:
            for package in (".", "./src"):
                package_path = path / package

                if (package_path / project_name / "__init__.py").exists():
                    version_files.append(
                        f"{package}/{project_name}/__init__.py"
                    )

                if (package_path / project_name / "__version__.py").exists():
                    version_files.append(
                        f"{package}/{project_name}/__version__.py"
                    )

                if (package_path / f"{project_name}.py").exists():
                    version_files.append(f"{package}/{project_name}.py")

    return tuple(version_files)


def run_post_bump_hook(
    config: ProjectConfig, *, is_dry_run: bool = False
) -> None:
    """Run post-bump hook after version files already updated.

    Read command to execute from project config, or if it is not specified
    run ``npm install`` or ``yarn install`` for JavaScript projects due to
    presence of lock files in project path.
    """
    path = config.path
    cmd = config.post_bump_hook

    if cmd is None and config.project_type == ProjectTypeEnum.javascript:
        if (path / FILE_PACKAGE_LOCK_JSON).exists():
            cmd = "npm install"
        elif (path / FILE_YARN_LOCK).exists():
            cmd = "yarn install"

    if cmd is None:
        return None

    echo_message(f"Running post-bump hook: {cmd}", is_dry_run=is_dry_run)
    if is_dry_run:
        return None

    subprocess.check_call(cmd, cwd=path, shell=True)


def update_changelog_file(
    config: ProjectConfig,
    next_version: Version,
    changelog: ChangeLog,
    *,
    is_dry_run: bool = False,
) -> None:
    """Update changelog file with new version.

    In most cases it just prepend new changelog on top of the file, but if next
    version is pre-release, do little trickery instead to include
    In Development header as well.
    """
    changelog_path = find_changelog_path(config)
    next_version_str = next_version.format(config=config)

    echo_message(
        f"Adding {next_version_str} release notes to {changelog_path.name} "
        "file",
        is_dry_run=is_dry_run,
    )
    if is_dry_run:
        return

    dev_header = in_development_header(
        next_version.version.format(), config.changelog_format_type_file
    )
    changelog_content = changelog.format(
        ChangeLogTypeEnum.changelog_file,
        config.changelog_format_type_file,
        is_pre_release=next_version.pre_release is not None,
    )

    if next_version.pre_release is None:
        next_version_changelog = "\n\n".join(
            (
                version_header(
                    next_version_str,
                    config.changelog_format_type_file,
                    is_pre_release=False,
                    include_date=config.changelog_file_include_date,
                ),
                changelog_content,
            )
        )
    else:
        next_version_changelog = "\n\n".join(
            (
                dev_header,
                version_header(
                    next_version_str,
                    config.changelog_format_type_file,
                    is_pre_release=True,
                    include_date=config.changelog_file_include_date,
                ),
                changelog_content,
            )
        )

    next_version_changelog = f"{next_version_changelog}\n\n"

    if not changelog_path.exists():
        changelog_path.write_text(f"{next_version_changelog.strip()}\n")
    else:
        if not update_file(
            changelog_path, f"{dev_header}\n\n", next_version_changelog
        ):
            changelog_path.write_text(
                "".join((next_version_changelog, changelog_path.read_text()))
            )


def update_file(
    path: Path,
    current_content: str,
    next_content: str,
) -> bool:
    """
    Attempt to read file if it exists and update current content to next
    content.

    If file does not exists, or current content not found - return False,
    otherwise return True.
    """
    if not path.exists():
        return False

    # TODO: Do not read whole file output for make replacement
    content = path.read_text()
    if current_content not in content:
        return False

    next_content = content.replace(current_content, next_content)
    echo_message(diff(content, next_content), is_dry_run=False)

    path.write_text(next_content)
    return True


def update_version_files(
    config: ProjectConfig,
    current_version: Optional[Version],
    next_version: Version,
    *,
    is_dry_run: bool = False,
) -> bool:
    """Update all project version files.

    If they not specified in config, attempt to guess them automatically.
    """
    if current_version is None:
        return False

    version_files = config.version_files
    if not version_files:
        version_files = guess_version_files(config)

    path = config.path
    current_version_str = current_version.format(config=config)
    next_version_str = next_version.format(config=config)

    updated: Set[bool] = set()

    for item in version_files:
        if item.startswith("..") or item.startswith("/"):
            raise ConfigError(
                "Version file outside of project directory is forbidden: "
                f"{item}"
            )

        echo_message(
            f"Updating version in {item}: {current_version_str} -> "
            f"{next_version_str}",
            is_dry_run=is_dry_run,
        )
        if is_dry_run:
            continue

        item_path = path.joinpath(item)
        updated.add(
            update_file(
                item_path,
                format_version_str(item_path, current_version_str),
                format_version_str(item_path, next_version_str),
            )
        )

    return len(updated) == 1 and updated.pop() is True
