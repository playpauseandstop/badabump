from difflib import ndiff


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
