import pytest

from badabump.cli.output import github_actions_output


@pytest.mark.parametrize(
    "value, expected",
    (
        ("Hello, world!", "Hello, world!"),
        ("$var", "$var"),
        ("`pwd`", "`pwd`"),
        ("Multi\nLine\nString", "Multi%0ALine%0AString"),
        ("Multi\r\nLine\r\nString", "Multi%0D%0ALine%0D%0AString"),
    ),
)
def test_github_actions_output(capsys, value, expected):
    github_actions_output("name", value)
    out, _ = capsys.readouterr()
    assert out == f"::set-output name=name::{expected}\n"
