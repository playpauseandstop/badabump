from pathlib import Path

import pytest

from badabump.cli.ci_app import main


@pytest.fixture()
def prepare_repository_for_release(create_git_repository):
    def factory() -> Path:
        git = create_git_repository(
            ("README.md", "# Project", "feat: Initial commit"),
            tag=(
                "v20.1.0",
                """20.1.0 Release

Features:
---------

- Initial release
    """,
            ),
        )
        return git.path

    return factory


def test_empty_subcommand(capsys):
    assert main([]) == 1

    captured = capsys.readouterr()
    assert (
        "ERROR: Please provide one of available subcommands. Exit..."
        in captured.err
    )
    assert captured.out == ""


def test_invalid_subcommand():
    with pytest.raises(SystemExit) as err:
        assert main(["invalid"])

    assert err.value.code == 2


@pytest.mark.parametrize("ref", (("v20.1.0", "refs/tags/v20.1.0")))
def test_prepare_release(
    capsys, github_output_path, prepare_repository_for_release, ref
):
    path = prepare_repository_for_release()
    assert main(["-C", str(path), "prepare_release", ref]) == 0

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    github_output = github_output_path.read_text()
    assert "tag_name<<EOF\nv20.1.0\nEOF\n" in github_output
    assert "is_pre_release<<EOF\nfalse\nEOF\n" in github_output
    assert "release_name<<EOF\n20.1.0 Release\nEOF\n" in github_output
    assert (
        "release_body<<EOF\nFeatures:\n---------\n\n- Initial release\nEOF\n"
    ) in github_output


def test_prepare_release_env_var(monkeypatch, prepare_repository_for_release):
    monkeypatch.setenv("GITHUB_REF", "refs/tags/v20.1.0")

    path = prepare_repository_for_release()
    assert main(["-C", str(path), "prepare_release"]) == 0


def test_prepare_tag(capsys, create_git_repository, github_output_path):
    git = create_git_repository(
        (
            "README.md",
            "# Project",
            """chore: 20.1.0 Release (#1)

Features:
---------

- Initial release

Signed-off-by: playpauseandstop <playpauseandstop@users.noreply.github.com>

Co-authored-by: playpauseandstop <playpauseandstop@users.noreply.github.com>
""",
        )
    )

    assert main(["-C", str(git.path), "prepare_tag"]) == 0

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    github_output = github_output_path.read_text()
    assert "tag_name<<EOF\nv20.1.0\nEOF\n" in github_output
    assert (
        "tag_message<<EOF\n20.1.0 Release\n\nFeatures:\n"
        "---------\n\n- Initial release\n\n\nEOF\n"
    ) in github_output


def test_prepare_tag_empty_body(capsys, create_git_repository):
    git = create_git_repository(
        ("README.md", "# Project", "feat: Initial commit")
    )
    assert main(["-C", str(git.path), "prepare_tag"]) == 1

    captured = capsys.readouterr()
    assert "ERROR: Last commit has empty body. Exit..." in captured.err
    assert captured.out == ""


def test_prepare_tag_invalid_commit(capsys, create_git_repository):
    git = create_git_repository(
        (
            "README.md",
            "# Project",
            """feat: Very important commit

Some text about the feature.

Issue: #1
""",
        )
    )
    assert main(["-C", str(git.path), "prepare_tag"]) == 1

    captured = capsys.readouterr()
    assert (
        "ERROR: Last commit has unexpected subject line. Exit..."
        in captured.err
    )
    assert captured.out == ""
