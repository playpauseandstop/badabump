import subprocess
from contextlib import suppress
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

import attr


@attr.dataclass(frozen=True, slots=True)
class Git:
    path: Path

    def list_commits(self, from_ref: str) -> Tuple[str, ...]:
        def iter_commtis(commit_ids: List[str]) -> Iterator[str]:
            for commit_id in commit_ids:
                yield self._check_output(
                    ["git", "log", "-1", "--format=%B", commit_id]
                )

        commit_ids = self._check_output(
            ["git", "log", "--format=%H", f"{from_ref}..HEAD"]
        ).splitlines()
        return tuple(iter_commtis(commit_ids))

    def retrieve_last_commit(self) -> str:
        return self._check_output(["git", "log", "-1", "--format=%B"])

    def retrieve_last_tag(self) -> str:
        return self._check_output(["git", "describe", "--abbrev=0", "--tags"])

    def retrieve_last_tag_or_none(self) -> Optional[str]:
        with suppress(subprocess.CalledProcessError, ValueError):
            return self.retrieve_last_tag()
        return None

    def retrieve_tag_body(self, tag: str) -> str:
        return self._check_output(
            ["git", "tag", "-l", "--format=%(body)", tag]
        )

    def retrieve_tag_subject(self, tag: str) -> str:
        return self._check_output(
            ["git", "tag", "-l", "--format=%(subject)", tag]
        )

    def _check_output(self, args: List[str]) -> str:
        maybe_output = subprocess.check_output(args, cwd=self.path)
        if maybe_output is not None:
            return maybe_output.strip().decode("utf-8")

        raise ValueError("git command return unexpected empty output")
