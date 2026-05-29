import io

import pytest

from badabump.cli.app import main
from badabump.enums import ProjectTypeEnum

BADABUMP_CONFIG_SEMVER_TOML = """[tool.badabump]
version_type = "semver"
"""

PACKAGE_JSON = """{{
    "name": "my-project",
    "version": "{version}",
    "dependencies": {{
        "another-project": "{version}"
    }}
}}
"""

PYPROJECT_TOML = """[project]
name = "my-project"
version = "{version}"
requires-python = ">=3.10,<4.0"
dependencies = [
    "another-project=={version}"
]
"""

PYPROJECT_TOML_POETRY = """[tool.poetry]
name = "my-project"
version = "{version}"

[tool.poetry.dependencies]
python = "^3.10"
another-project = "{version}"
"""

PYPROJECT_TOML_POETRY_DEPENDENCIES = """[project]
name = "my-project"
version = "{version}"

[tool.poetry.dependencies]
python = "^3.10"
another-project = "{version}"
"""


@pytest.mark.parametrize(
    "pyproject_toml",
    (
        PYPROJECT_TOML,
        PYPROJECT_TOML_POETRY,
        PYPROJECT_TOML_POETRY_DEPENDENCIES,
    ),
)
def test_breaking_change_dry_run(
    capsys, create_git_commit, create_git_repository, pyproject_toml: str
):
    git = create_git_repository(
        (
            "pyproject.toml",
            BADABUMP_CONFIG_SEMVER_TOML
            + pyproject_toml.format(version="1.0.0"),
            "feat: Initial commit",
        ),
        tag=("v1.0.0", "1.0.0 Release"),
    )
    path = git.path

    (path / "file.txt").write_text("")

    create_git_commit(
        path,
        """feat(auth): Implement login flow

BREAKING CHANGE: Now it is possible to log into backend using API endpoint.

Issue: AUTH-1
""",
    )
    assert main(["-C", str(path), "-d"]) == 0

    assert (path / "CHANGELOG.md").exists() is False

    captured = capsys.readouterr()
    assert captured.err == ""
    assert "Next version: 2.0.0" in captured.out


@pytest.mark.parametrize(
    "file_name, content, version, next_version",
    (
        (
            "pyproject.toml",
            BADABUMP_CONFIG_SEMVER_TOML
            + PYPROJECT_TOML.format(version="1.0.0"),
            "1.0.0",
            "1.0.1",
        ),
        (
            "pyproject.toml",
            BADABUMP_CONFIG_SEMVER_TOML
            + PYPROJECT_TOML_POETRY.format(version="1.0.0"),
            "1.0.0",
            "1.0.1",
        ),
        (
            "pyproject.toml",
            BADABUMP_CONFIG_SEMVER_TOML
            + PYPROJECT_TOML_POETRY_DEPENDENCIES.format(version="1.0.0"),
            "1.0.0",
            "1.0.1",
        ),
        (
            "package.json",
            PACKAGE_JSON.format(version="22.1.0"),
            "22.1.0",
            "22.1.1",
        ),
    ),
)
def test_ci_output(
    capsys,
    time_machine,
    create_git_commit,
    create_git_repository,
    github_output_path,
    file_name,
    content,
    version,
    next_version,
):
    time_machine.move_to("2022-12-31T00:00:00+00:00")

    git = create_git_repository(
        (file_name, content, "feat: Initial commit"),
        tag=(f"v{version}", f"{version} Release"),
    )
    path = git.path

    (path / "file.txt").write_text("")

    create_git_commit(path, "fix(auth): Important login flow fix")
    assert main(["-C", str(path), "--ci"]) == 0

    captured = capsys.readouterr()
    assert captured.out != ""
    assert captured.err == ""

    github_output = github_output_path.read_text()
    assert f"current_tag<<EOF\nv{version}\nEOF\n" in github_output
    assert f"current_version<<EOF\n{version}\nEOF\n" in github_output
    assert f"next_version<<EOF\n{next_version}\n" in github_output

    changelog = (path / "CHANGELOG.md").read_text()
    assert f"# {next_version}" in changelog

    next_content = (path / file_name).read_text()
    if file_name == "pyproject.toml":
        assert f'version = "{next_version}"' in next_content
        if "dependencies = [" in next_content:
            assert f'    "another-project=={version}"' in next_content
        else:
            assert f'another-project = "{version}"' in next_content
    else:
        assert f'"version": "{next_version}"' in next_content
        assert f'"another-project": "{version}"' in next_content


@pytest.mark.parametrize(
    "project_type, file_name, template, version, expected",
    (
        (
            ProjectTypeEnum.python,
            "pyproject.toml",
            PYPROJECT_TOML,
            "20.1.0",
            "- Initial release",
        ),
        (
            ProjectTypeEnum.python,
            "pyproject.toml",
            PYPROJECT_TOML_POETRY,
            "20.1.0",
            "- Initial release",
        ),
        (
            ProjectTypeEnum.python,
            "pyproject.toml",
            PYPROJECT_TOML_POETRY_DEPENDENCIES,
            "20.1.0",
            "- Initial release",
        ),
        (
            ProjectTypeEnum.python,
            "pyproject.toml",
            PYPROJECT_TOML,
            "20.1.0a0",
            "- Initial pre-release",
        ),
        (
            ProjectTypeEnum.python,
            "pyproject.toml",
            PYPROJECT_TOML_POETRY,
            "20.1.0a0",
            "- Initial pre-release",
        ),
        (
            ProjectTypeEnum.python,
            "pyproject.toml",
            PYPROJECT_TOML_POETRY_DEPENDENCIES,
            "20.1.0a0",
            "- Initial pre-release",
        ),
        (
            ProjectTypeEnum.javascript,
            "package.json",
            PACKAGE_JSON,
            "20.1.0",
            "- Initial release",
        ),
        (
            ProjectTypeEnum.javascript,
            "package.json",
            PACKAGE_JSON,
            "20.1.0-alpha.0",
            "- Initial pre-release",
        ),
    ),
)
def test_initial_release(
    monkeypatch,
    create_git_repository,
    project_type,
    file_name,
    template,
    version,
    expected,
):
    monkeypatch.setattr("sys.stdin", io.StringIO("y"))

    content = template.format(version=version)
    git = create_git_repository((file_name, content, "feat: Initial commit"))
    path = git.path

    assert main(["-C", str(path)]) == 0

    assert git.retrieve_tag_subject(f"v{version}") == ""
    assert (path / "CHANGELOG.md").exists()

    changelog = (path / "CHANGELOG.md").read_text()
    assert version in changelog
    assert expected in changelog

    assert (path / file_name).read_text() == content


@pytest.mark.parametrize(
    "pyproject_toml",
    (
        PYPROJECT_TOML,
        PYPROJECT_TOML_POETRY,
        PYPROJECT_TOML_POETRY_DEPENDENCIES,
    ),
)
@pytest.mark.parametrize(
    "changelog_content", ("", "# 1.1.0 (In Development)\n\n")
)
def test_minor_change(
    capsys,
    monkeypatch,
    create_git_commit,
    create_git_repository,
    pyproject_toml: str,
    changelog_content: str,
):
    monkeypatch.setattr("sys.stdin", io.StringIO("y"))

    git = create_git_repository(
        (
            "pyproject.toml",
            BADABUMP_CONFIG_SEMVER_TOML
            + pyproject_toml.format(version="1.0.0"),
            "feat: Initial commit",
        ),
        tag=("v1.0.0", "1.0.0 Release"),
    )
    path = git.path

    (path / "file.ext").write_text("")
    (path / "CHANGELOG.md").write_text(
        f"""{changelog_content}# 1.0.0 (2020-11-08)

- Initial release
"""
    )

    create_git_commit(path, "feat: Update very important part of the system")
    assert main(["-C", str(path)]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert "Current tag: v1.0.0\n" in captured.out
    assert "Current version: 1.0.0\n" in captured.out
    assert "Next version: 1.1.0\n" in captured.out


@pytest.mark.parametrize(
    "pyproject_toml",
    (
        PYPROJECT_TOML,
        PYPROJECT_TOML_POETRY,
        PYPROJECT_TOML_POETRY_DEPENDENCIES,
    ),
)
def test_no_commits(
    capsys, create_git_commit, create_git_repository, pyproject_toml: str
):
    git = create_git_repository(
        (
            "pyproject.toml",
            BADABUMP_CONFIG_SEMVER_TOML
            + pyproject_toml.format(version="1.0.0"),
            "feat: Initial commit",
        ),
        tag=("v1.0.0", "1.0.0 Release"),
    )

    assert main(["-C", str(git.path)]) == 1

    captured = capsys.readouterr()
    assert "ERROR: No commits found after: 'v1.0.0'. Exit..." in captured.err
    assert "Next version: " not in captured.out


@pytest.mark.parametrize(
    "pyproject_toml",
    (
        PYPROJECT_TOML,
        PYPROJECT_TOML_POETRY,
        PYPROJECT_TOML_POETRY_DEPENDENCIES,
    ),
)
def test_no_commits_pre_release(
    capsys, monkeypatch, create_git_repository, pyproject_toml: str
):
    monkeypatch.setattr("sys.stdin", io.StringIO("y"))

    content = BADABUMP_CONFIG_SEMVER_TOML + pyproject_toml.format(
        version="1.0.0rc0"
    )

    git = create_git_repository(
        (
            "pyproject.toml",
            content,
            "feat: Initial commit",
        ),
        tag=("v1.0.0rc0", "1.0.0rc0 Release"),
    )
    path = git.path

    assert main(["-C", str(path)]) == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert "Next version: 1.0.0\n" in captured.out

    assert content != (path / "pyproject.toml").read_text()


@pytest.mark.parametrize(
    "pyproject_toml",
    (
        PYPROJECT_TOML,
        PYPROJECT_TOML_POETRY,
        PYPROJECT_TOML_POETRY_DEPENDENCIES,
    ),
)
def test_wrong_answer(
    capsys, monkeypatch, create_git_repository, pyproject_toml: str
):
    monkeypatch.setattr("sys.stdin", io.StringIO("n"))

    content = BADABUMP_CONFIG_SEMVER_TOML + pyproject_toml.format(
        version="1.0.0rc0"
    )

    git = create_git_repository(
        (
            "pyproject.toml",
            content,
            "feat: Initial commit",
        ),
        tag=("v1.0.0rc0", "1.0.0rc0 Release"),
    )
    path = git.path

    assert main(["-C", str(path)]) == 0

    captured = capsys.readouterr()
    assert "OK! OK! Exit..." in captured.out

    assert content == (path / "pyproject.toml").read_text()
