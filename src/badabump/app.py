import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from . import __app__, __version__
from .changelog import ChangeLog
from .commands import (
    run_post_bump_hook,
    update_changelog_file,
    update_version_files,
)
from .configs import ProjectConfig, UpdateConfig
from .enums import ChangeLogTypeEnum
from .git import Git
from .versions import Version


Argv = Sequence[str]


def create_update_config(
    changelog: ChangeLog, is_pre_release: bool
) -> UpdateConfig:
    kwargs = {
        "is_breaking_change": False,
        "is_minor_change": False,
        "is_micro_change": False,
        "is_pre_release": is_pre_release,
    }

    if changelog.has_breaking_change:
        kwargs["is_breaking_change"] = True
    elif changelog.has_minor_change:
        kwargs["is_minor_change"] = True
    elif changelog.has_micro_change:
        kwargs["is_micro_change"] = True

    return UpdateConfig(**kwargs)


def echo(
    label: str, value: str, *, is_ci: bool = False, ci_name: str = None
) -> None:
    if is_ci and ci_name:
        github_actions_output(ci_name, value)
    else:
        print(f"{label}{value}")


def github_actions_output(name: str, value: str) -> None:
    value = value.replace("%", "%25")
    value = value.replace("\n", "%0A")
    value = value.replace("\r", "%0D")
    print(f"::set-output name={name}::{value}")


def parse_args(argv: Argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=__app__,
        description=(
            "Bump project version number basing on conventional commits from "
            "latest tag."
        ),
    )
    parser.add_argument(
        "-v", "--version", action="version", version=__version__
    )
    parser.add_argument(
        "-C",
        "--path",
        default=Path.cwd(),
        help="Directory with project. By default: current working directory",
        type=Path,
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        default=False,
        dest="is_dry_run",
        help="Only show updates, but do not apply them.",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        default=os.getenv("CI") is not None,
        dest="is_ci",
        help=f"Run {__app__} in CI mode.",
    )
    parser.add_argument(
        "--pre",
        action="store_true",
        default=False,
        dest="is_pre_release",
        help="Pre-release change. By default: False",
    )
    return parser.parse_args(argv)


def main(argv: Argv = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    # Initialize project config
    project_config = ProjectConfig.from_path(args.path)

    # Read latest git tag and parse current version
    git = Git(path=project_config.path)

    latest_tag = git.retrieve_latest_tag()
    echo("Current tag: ", latest_tag, is_ci=args.is_ci, ci_name="current_tag")

    current_version = Version.from_tag(latest_tag, config=project_config)
    echo(
        "Current version: ",
        current_version.format(config=project_config),
        is_ci=args.is_ci,
        ci_name="current_version",
    )

    # Read commits from last tag
    try:
        git_commits = git.list_commits(latest_tag)
        if not git_commits:
            raise ValueError("No commits, nothing to release :(")
    except ValueError:
        print(
            f"ERROR: No commits found after: {latest_tag!r}. Exit...",
            file=sys.stderr,
        )
        return 1

    # Create changelog using commits from last tag
    changelog = ChangeLog.from_git_commits(git_commits)
    echo(
        "\nChangeLog\n\n",
        changelog.format(
            ChangeLogTypeEnum.git_commit,
            project_config.changelog_format_type_git,
        ),
        is_ci=args.is_ci,
        ci_name="changelog",
    )

    # Supply update config and guess next version
    update_config = create_update_config(changelog, args.is_pre_release)

    next_version = current_version.update(update_config)
    echo(
        "\nNext version: ",
        next_version.format(config=project_config),
        is_ci=args.is_ci,
        ci_name="next_version",
    )

    # Applying changes to version files
    if not args.is_ci and not args.is_dry_run:
        if (
            input("Are you sure to update version files? [y/N] ").lower()
            != "y"
        ):
            print("OK! OK! Exit...")
            return 0

    update_version_files(
        project_config,
        current_version,
        next_version,
        is_dry_run=args.is_dry_run,
    )

    # Run post-bump hook
    run_post_bump_hook(project_config, is_dry_run=args.is_dry_run)

    # Update changelog
    update_changelog_file(
        project_config, next_version, changelog, is_dry_run=args.is_dry_run
    )

    print("All OK!")
    return 0
