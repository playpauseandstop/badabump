from __future__ import annotations

import dataclasses
import subprocess
from contextlib import suppress
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Git:
    path: Path

    def list_commits(self, from_ref: str) -> tuple[str, ...]:
        def iter_commtis(commit_ids: list[str]) -> Iterator[str]:
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

    def retrieve_last_tag_or_none(self) -> Union[str, None]:
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

    def _check_output(self, args: list[str]) -> str:
        maybe_output = subprocess.check_output(args, cwd=self.path)
        if maybe_output is not None:
            return maybe_output.strip().decode("utf-8")

        raise ValueError("git command return unexpected empty output")
