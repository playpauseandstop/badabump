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
def test_prepare_release(capsys, prepare_repository_for_release, ref):
    path = prepare_repository_for_release()
    assert main(["-C", str(path), "prepare_release", ref]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""

    assert "::set-output name=tag_name::v20.1.0"
    assert "::set-output name=is_pre_release::false" in captured.out
    assert "::set-output name=release_name::20.1.0 Release" in captured.out
    assert (
        "::set-output name=release_body::Features:%0A---------"
        "%0A%0A- Initial release"
    ) in captured.out


def test_prepare_release_env_var(monkeypatch, prepare_repository_for_release):
    monkeypatch.setenv("GITHUB_REF", "refs/tags/v20.1.0")

    path = prepare_repository_for_release()
    assert main(["-C", str(path), "prepare_release"]) == 0


def test_prepare_tag(capsys, create_git_repository):
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
    assert captured.err == ""

    assert "::set-output name=tag_name::v20.1.0" in captured.out
    assert (
        "::set-output name=tag_message::20.1.0 Release%0A%0AFeatures:"
        "%0A---------%0A%0A- Initial release%0A"
    ) in captured.out


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
