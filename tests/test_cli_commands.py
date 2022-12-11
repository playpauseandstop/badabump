from pathlib import Path
from unittest.mock import Mock

import pytest

from badabump.cli.commands import (
    find_changelog_path,
    guess_version_files,
    run_post_bump_hook,
    update_file,
    update_version_files,
)
from badabump.configs import ProjectConfig
from badabump.enums import FormatTypeEnum, ProjectTypeEnum
from badabump.exceptions import ConfigError
from badabump.versions import Version


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.mark.parametrize(
    "format_type, file_name",
    (
        (FormatTypeEnum.markdown, "CHANGELOG.md"),
        (FormatTypeEnum.rst, "CHANGELOG.rst"),
    ),
)
def test_find_changelog_path(tmpdir, format_type, file_name):
    path = Path(tmpdir)
    (path / file_name).write_text("# 1.0.0 Release (YYYY-MM-DD)")
    assert (
        find_changelog_path(
            ProjectConfig(path=path, changelog_format_type_file=format_type)
        )
        == path / file_name
    )


@pytest.mark.parametrize(
    "format_type, expected",
    (
        (FormatTypeEnum.markdown, "CHANGELOG.md"),
        (FormatTypeEnum.rst, "CHANGELOG.rst"),
    ),
)
def test_find_changelog_path_no_file(tmpdir, format_type, expected):
    path = Path(tmpdir)
    assert (
        find_changelog_path(
            ProjectConfig(path=path, changelog_format_type_file=format_type)
        )
        == path / expected
    )


def test_guess_javascript_version_files(tmpdir):
    assert guess_version_files(
        ProjectConfig(
            path=Path(tmpdir), project_type=ProjectTypeEnum.javascript
        )
    ) == ("package.json",)


@pytest.mark.parametrize(
    "files, expected",
    (
        ((), ("pyproject.toml",)),
        (
            ("my_project.py",),
            ("pyproject.toml", "my_project.py"),
        ),
        (
            ("my_project/__init__.py", "my_project/__version__.py"),
            (
                "pyproject.toml",
                "my_project/__init__.py",
                "my_project/__version__.py",
            ),
        ),
        (
            ("src/my-project/__init__.py", "src/my-project/__version__.py"),
            (
                "pyproject.toml",
                "src/my-project/__init__.py",
                "src/my-project/__version__.py",
            ),
        ),
    ),
)
def test_guess_python_version_files(tmpdir, files, expected):
    path = Path(tmpdir)

    (path / "pyproject.toml").write_text(
        """[tool.poetry]
name = "my-project"
version = "1.0.0"
"""
    )

    for item in files:
        item_path = path.joinpath(item)
        ensure_dir(item_path.parent)
        item_path.write_text("")

    assert (
        guess_version_files(
            ProjectConfig(path=path, project_type=ProjectTypeEnum.python)
        )
        == expected
    )


def test_guess_python_version_files_invalid_poetry_config(tmpdir):
    path = Path(tmpdir)
    (path / "pyproject.toml").write_text(
        """[tool.poetry]
version = "1.0.0"
"""
    )
    assert guess_version_files(
        ProjectConfig(path=path, project_type=ProjectTypeEnum.python)
    ) == ("pyproject.toml",)


def test_guess_python_version_files_no_pyproject_toml(tmpdir):
    assert (
        guess_version_files(
            ProjectConfig(
                path=Path(tmpdir), project_type=ProjectTypeEnum.python
            )
        )
        == ()
    )


@pytest.mark.parametrize(
    "file_name, expected",
    (("package-lock.json", "npm install"), ("yarn.lock", "yarn install")),
)
def test_run_post_bump_hook(capsys, monkeypatch, tmpdir, file_name, expected):
    monkeypatch.setattr("subprocess.check_call", Mock())

    path = Path(tmpdir)
    (path / file_name).write_text("")

    run_post_bump_hook(
        ProjectConfig(path=path, project_type=ProjectTypeEnum.javascript),
        is_dry_run=False,
    )


@pytest.mark.parametrize(
    "file_name, expected",
    (("package-lock.json", "npm install"), ("yarn.lock", "yarn install")),
)
def test_run_post_bump_hook_dry_run(capsys, tmpdir, file_name, expected):
    path = Path(tmpdir)
    (path / file_name).write_text("")

    run_post_bump_hook(
        ProjectConfig(path=path, project_type=ProjectTypeEnum.javascript),
        is_dry_run=True,
    )

    captured = capsys.readouterr()
    assert captured.err == ""
    assert expected in captured.out


def test_update_file_does_not_exist(tmpdir):
    assert (
        update_file(Path(tmpdir) / "does-not-exist.txt", "one", "two") is False
    )


def test_update_version_files_no_current_version(tmpdir):
    config = ProjectConfig(path=Path(tmpdir))
    next_version = Version.from_tag("v20.1.0", config=config)
    assert update_version_files(config, None, next_version) is False


def test_update_version_files_with_version_files(tmpdir):
    config = ProjectConfig(
        path=Path(tmpdir), version_files=("pyproject.toml",)
    )
    current_version = Version.from_tag("v20.1.0", config=config)
    next_version = Version.from_tag("v20.1.1", config=config)
    assert update_version_files(config, current_version, next_version) is False


@pytest.mark.parametrize(
    "invalid_files", (("../pyproject.toml",), ("/tmp/pyproject.toml",))
)
def test_update_version_files_with_invalid_version_files(
    tmpdir, invalid_files
):
    config = ProjectConfig(path=Path(tmpdir), version_files=invalid_files)

    current_version = Version.from_tag("v20.1.0", config=config)
    next_version = Version.from_tag("v20.1.1", config=config)

    with pytest.raises(ConfigError):
        update_version_files(config, current_version, next_version)
