import io

import pytest

from badabump.cli.app import main
from badabump.enums import ProjectTypeEnum


BADABUMP_CONFIG_SEMVER_TOML = """[tool.badabump]
version_type = "semver"
"""

PACKAGE_JSON = """{{
    "name": "my-project",
    "version": "{version}"
}}
"""

PYPROJECT_TOML = """[tool.poetry]
name = "my-project"
version = "{version}"
"""


def test_ci_output(capsys, create_git_commit, create_git_repository):
    git = create_git_repository(
        (
            "pyproject.toml",
            BADABUMP_CONFIG_SEMVER_TOML
            + PYPROJECT_TOML.format(version="1.0.0"),
            "feat: Initial commit",
        ),
        tag=("v1.0.0", "1.0.0 Release"),
    )
    path = git.path

    (path / "file.txt").write_text("")

    create_git_commit(path, "fix(auth): Important login flow fix")
    main(["-C", str(path), "--ci"])

    captured = capsys.readouterr()
    assert captured.err == ""

    assert "::set-output name=current_tag::v1.0.0" in captured.out
    assert "::set-output name=current_version::1.0.0" in captured.out
    assert "::set-output name=next_version::1.0.1" in captured.out

    changelog = (path / "CHANGELOG.md").read_text()
    assert "# 1.0.1" in changelog

    pyproject_toml = (path / "pyproject.toml").read_text()
    assert 'version = "1.0.1"' in pyproject_toml


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
            PYPROJECT_TOML,
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

    main(["-C", str(path)])

    assert git.retrieve_tag_subject(f"v{version}") == ""
    assert (path / "CHANGELOG.md").exists()

    changelog = (path / "CHANGELOG.md").read_text()
    assert version in changelog
    assert expected in changelog

    assert (path / file_name).read_text() == content
