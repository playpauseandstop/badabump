import io

import pytest

from badabump.cli.app import main
from badabump.enums import ProjectTypeEnum


PACKAGE_JSON = """{{
    "name": "my-project",
    "version": "{version}"
}}
"""

PYPROJECT_TOML = """[tool.poetry]
name = "my-project"
version = "{version}"
"""


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
