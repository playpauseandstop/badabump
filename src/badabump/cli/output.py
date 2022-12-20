import os
from difflib import ndiff
from typing import Union


EMPTY = "-"


def diff(current_content: str, next_content: str) -> str:
    items = ndiff(
        current_content.splitlines(keepends=True),
        next_content.splitlines(keepends=True),
    )
    return "".join(item for item in items if item.startswith(("-", "+", "?")))


def echo_message(message: str, *, is_dry_run: bool) -> None:
    prefix = "[DRY-RUN] " if is_dry_run else ""
    print(f"{prefix}{message}")


def echo_value(
    label: str,
    value: str,
    *,
    is_ci: bool = False,
    ci_name: Union[str, None] = None,
) -> None:
    if is_ci and ci_name:
        github_actions_output(ci_name, value)
    else:
        print(f"{label}{value}")


def github_actions_output(name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a+") as github_output_handler:
        github_output_handler.write(f"{name}<<EOF\n")
        github_output_handler.write(value)
        github_output_handler.write("\nEOF\n")
