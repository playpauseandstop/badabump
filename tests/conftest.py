import subprocess
from pathlib import Path
from typing import Tuple, Union

import pytest

from badabump.git import Git


CommitTuple = Tuple[str, Union[str, None], str]
TagTuple = Tuple[str, str]


@pytest.fixture(scope="function", autouse=True)
def setup_github_output_env_var(monkeypatch, github_output_path):
    monkeypatch.setenv("GITHUB_OUTPUT", str(github_output_path))
    yield


@pytest.fixture(scope="function")
def create_git_commit():
    def factory(path: Path, commit: str) -> None:
        subprocess.check_call(["git", "add", "."], cwd=path)
        subprocess.check_call(["git", "commit", "-m", commit], cwd=path)

    return factory


@pytest.fixture(scope="function")
def create_git_repository(tmpdir, create_git_commit, create_git_tag):
    def factory(*commits: CommitTuple, tag: TagTuple = None) -> Git:
        path = Path(tmpdir)

        subprocess.check_call(["git", "init"], cwd=path)

        for file_name, content, commit in commits:
            (path / file_name).write_text(content or "")
            create_git_commit(path, commit)

        if tag is not None:
            create_git_tag(path, *tag)

        return Git(path=path)

    return factory


@pytest.fixture(scope="function")
def create_git_tag():
    def factory(path: Path, tag: str, message: str) -> None:
        subprocess.check_call(
            ["git", "tag", "-a", tag, "-m", message], cwd=path
        )

    return factory


@pytest.fixture(scope="function")
def github_output_path(tmp_path) -> Path:
    path = Path(tmp_path) / "github-output.txt"
    if not path.exists():
        path.write_text("")
    return path
