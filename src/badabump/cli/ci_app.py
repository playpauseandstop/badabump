import argparse
import json
import os
import sys
from typing import cast

from badabump import __app__, __version__
from badabump.annotations import Argv
from badabump.cleaners import clean_body, clean_commit_subject, clean_tag_ref
from badabump.cli.arguments import add_path_argument
from badabump.cli.output import github_actions_output
from badabump.configs import ProjectConfig
from badabump.git import Git
from badabump.regexps import to_regexp
from badabump.versions import Version


def parse_args(argv: Argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=f"{__app__}-ci",
        description=(
            "Useful commands for dealing with release commits & tags at CI"
        ),
    )
    parser.add_argument(
        "-v", "--version", action="version", version=__version__
    )
    add_path_argument(parser)

    subparsers = parser.add_subparsers()

    prepare_tag_parser = subparsers.add_parser("prepare_tag")
    prepare_tag_parser.set_defaults(func=prepare_tag)

    prepare_release_parser = subparsers.add_parser("prepare_release")
    prepare_release_parser.add_argument(
        "ref",
        default=os.getenv("GITHUB_REF"),
        help="Tag reference. By default: GITHUB_REF env var",
        metavar="REF",
        nargs="?",
    )
    prepare_release_parser.set_defaults(func=prepare_release)

    return parser.parse_args(argv)


def prepare_release(args: argparse.Namespace, *, config: ProjectConfig) -> int:
    git = Git(path=config.path)

    tag_ref = clean_tag_ref(args.ref)
    version = Version.from_tag(tag_ref, config=config)
    github_actions_output("tag_name", tag_ref)
    github_actions_output(
        "is_pre_release", json.dumps(version.pre_release is not None)
    )

    tag_subject = git.retrieve_tag_subject(tag_ref)
    github_actions_output("release_name", tag_subject)

    tag_body = git.retrieve_tag_body(tag_ref)
    github_actions_output("release_body", tag_body)

    return 0


def prepare_tag(args: argparse.Namespace, *, config: ProjectConfig) -> int:
    git = Git(path=config.path)
    git_commit = git.retrieve_last_commit()
    try:
        raw_subject, _, *body = git_commit.splitlines()
    except ValueError:
        print("ERROR: Last commit has empty body. Exit...", file=sys.stderr)
        return 1

    expected_re = to_regexp(config.pr_title_format)
    matched = expected_re.match(clean_commit_subject(raw_subject))
    if matched is None:
        print(
            "ERROR: Last commit has unexpected subject line. Exit...",
            file=sys.stderr,
        )
        return 1

    version = matched.groupdict()["version"]
    github_actions_output(
        "tag_name", config.tag_format.format(version=version)
    )
    github_actions_output(
        "tag_message",
        "\n\n".join(
            (
                config.tag_subject_format.format(version=version),
                clean_body(body),
            )
        ),
    )

    return 0


def main(argv: Argv = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    # TODO: Fix this by providing required flag on adding subparsers
    if getattr(args, "func", None) is None:
        print(
            "ERROR: Please provide one of available subcommands. Exit...",
            file=sys.stderr,
        )
        return 1

    config = ProjectConfig.from_path(args.path)
    return cast(int, args.func(args, config=config))
