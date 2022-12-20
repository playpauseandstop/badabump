import pytest

from badabump.cli.output import github_actions_output


@pytest.mark.parametrize(
    "value, expected",
    (
        ("Hello, world!", "Hello, world!"),
        ("$var", "$var"),
        ("`pwd`", "`pwd`"),
        ("Multi\nLine\nString", "Multi\nLine\nString"),
        ("Multi\r\nLine\r\nString", "Multi\nLine\nString"),
    ),
)
def test_github_actions_output(capsys, github_output_path, value, expected):
    github_actions_output("name", value)

    # Check that nothing written into stdout / stderr
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    # But GITHUB_OUTPUT file contains proper context
    assert github_output_path.read_text() == f"name<<EOF\n{expected}\nEOF\n"
