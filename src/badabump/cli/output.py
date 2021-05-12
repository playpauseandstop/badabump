from difflib import ndiff


EMPTY = "-"
VALUE_ESCAPE_MAPPING = (("%", "%25"), ("\n", "%0A"), ("\r", "%0D"))


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
    for symbol, code in VALUE_ESCAPE_MAPPING:
        value = value.replace(symbol, code)
    print(f"::set-output name={name}::{value}")
