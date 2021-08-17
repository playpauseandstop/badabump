import datetime
import logging
import re
from typing import Iterator, List, Optional, Tuple

import attr

from badabump.enums import ChangeLogTypeEnum, FormatTypeEnum


BREAKING_CHANGE_IN_BODY = "BREAKING CHANGE:"
BREAKING_CHANGE_IN_COMMIT_TYPE = "!"

CHANGELOG_EMPTY = "No changes since last pre-release"

COMMIT_TYPE_FEATURE = "feat"
COMMIT_TYPE_FIX = "fix"
COMMIT_TYPE_REFACTOR = "refactor"
COMMIT_TYPE_UNKNOWN = "unknown"

COMMIT_TYPE_SUBJECT_RE = re.compile(
    r"^(?P<commit_type>[^\:]+)\: (?P<description>.+)$"
)
COMMIT_TYPE_SCOPE_RE = re.compile(
    r"^(?P<commit_type>[^\(]+)\((?P<scope>[^\)]+)\)$"
)

ISSUE_RE = re.compile(
    r"^(Closes|Fixes|Issue|Ref|Relates): (?P<issue>.+)$", re.M
)

logger = logging.getLogger(__name__)


@attr.dataclass(frozen=True, slots=True)
class ConventionalCommit:
    raw_commit_type: str
    description: str

    body: Optional[str] = None

    @property
    def clean_commit_type(self) -> str:
        commit_type = self.raw_commit_type
        if commit_type[-1] == BREAKING_CHANGE_IN_COMMIT_TYPE:
            return commit_type[:-1]
        return commit_type

    @property
    def commit_type(self) -> str:
        commit_type = self.clean_commit_type

        maybe_matched = COMMIT_TYPE_SCOPE_RE.match(commit_type)
        if maybe_matched is not None:
            return maybe_matched.groupdict()["commit_type"]

        return commit_type

    def format(  # noqa: A003
        self, format_type: FormatTypeEnum, *, ignore_footer_urls: bool = True
    ) -> str:
        prefix = ""
        if self.scope:
            prefix = f"({bold(self.scope)}) "

        if self.is_breaking_change:
            prefix = f"{bold(BREAKING_CHANGE_IN_BODY)} {prefix}"

        issues = self.issues
        if issues and ignore_footer_urls:
            issues = tuple(item for item in issues if not is_url(item))
        if issues:
            prefix = f'[{", ".join(issues)}] {prefix}'

        return f"{prefix}{self.description}"

    @classmethod
    def from_git_commit(
        cls, git_commit: str, *, strict: bool = True
    ) -> "ConventionalCommit":
        subject, *body = git_commit.splitlines()
        body_str = "\n".join(body[1:]) if body else None

        maybe_matched = COMMIT_TYPE_SUBJECT_RE.match(subject)
        if maybe_matched is not None:
            matched_dict = maybe_matched.groupdict()
            return cls(
                raw_commit_type=matched_dict["commit_type"],
                description=matched_dict["description"].strip(),
                body=body_str,
            )

        if strict:
            raise ValueError(
                "Unable to parse git commit as conventional commit"
            )

        logger.warning(
            "WARNING: Unable to parse git commit as conventional commit: %r",
            subject,
            extra={"subject": subject},
        )
        return cls(
            raw_commit_type=COMMIT_TYPE_UNKNOWN,
            description=subject,
            body=body_str,
        )

    @property
    def is_breaking_change(self) -> bool:
        return self.raw_commit_type[-1] == BREAKING_CHANGE_IN_COMMIT_TYPE or (
            self.body is not None and BREAKING_CHANGE_IN_BODY in self.body
        )

    @property
    def issues(self) -> Tuple[str, ...]:
        if self.body is None:
            return ()
        return tuple(item.strip() for _, item in ISSUE_RE.findall(self.body))

    @property
    def scope(self) -> Optional[str]:
        commit_type = self.clean_commit_type

        maybe_matched = COMMIT_TYPE_SCOPE_RE.match(commit_type)
        if maybe_matched is not None:
            return maybe_matched.groupdict()["scope"]

        return None


@attr.dataclass(frozen=True, slots=True)
class ChangeLog:
    commits: Tuple[ConventionalCommit, ...]

    feature_commits: Tuple[ConventionalCommit, ...] = attr.ib(init=False)
    fix_commits: Tuple[ConventionalCommit, ...] = attr.ib(init=False)
    refactor_commits: Tuple[ConventionalCommit, ...] = attr.ib(init=False)
    other_commits: Tuple[ConventionalCommit, ...] = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        feature_commits: List[ConventionalCommit] = []
        fix_commits: List[ConventionalCommit] = []
        refactor_commits: List[ConventionalCommit] = []
        other_commits: List[ConventionalCommit] = []

        for commit in self.commits:
            if commit.commit_type == COMMIT_TYPE_FEATURE:
                feature_commits.append(commit)
            elif commit.commit_type == COMMIT_TYPE_FIX:
                fix_commits.append(commit)
            elif commit.commit_type == COMMIT_TYPE_REFACTOR:
                refactor_commits.append(commit)
            else:
                other_commits.append(commit)

        object.__setattr__(self, "feature_commits", tuple(feature_commits))
        object.__setattr__(self, "fix_commits", tuple(fix_commits))
        object.__setattr__(self, "refactor_commits", tuple(refactor_commits))
        object.__setattr__(self, "other_commits", tuple(other_commits))

    def format(  # noqa: A003
        self,
        changelog_type: ChangeLogTypeEnum,
        format_type: FormatTypeEnum,
        *,
        is_pre_release: bool = False,
        ignore_footer_urls: bool = True,
    ) -> str:
        if not self.commits:
            return CHANGELOG_EMPTY

        is_git_commit = changelog_type == ChangeLogTypeEnum.git_commit
        is_rst = format_type == FormatTypeEnum.rst

        def format_block(
            label: str, commits: Tuple[ConventionalCommit, ...]
        ) -> Optional[str]:
            if not commits:
                return None

            header: str
            if is_rst:
                header = bold(label)
            elif is_git_commit:
                header = markdown_h2(label, git_safe=True)
            elif is_pre_release:
                header = markdown_h3(label)
            else:
                header = markdown_h2(label)

            breaking_items = format_commits(
                item for item in commits if item.is_breaking_change
            )
            regular_items = format_commits(
                item for item in commits if not item.is_breaking_change
            )
            items = "\n".join(
                item for item in (breaking_items, regular_items) if item
            )

            return "\n\n".join((header, items))

        def format_commits(commits: Iterator[ConventionalCommit]) -> str:
            return "\n".join(
                ul_li(
                    item.format(
                        format_type, ignore_footer_urls=ignore_footer_urls
                    )
                )
                for item in commits
            )

        features = format_block("Features:", self.feature_commits)
        fixes = format_block("Fixes:", self.fix_commits)
        refactor = format_block("Refactoring:", self.refactor_commits)
        others = format_block("Other:", self.other_commits)

        return "\n\n".join(
            item for item in (features, fixes, refactor, others) if item
        )

    @classmethod
    def from_git_commits(
        cls, git_commits: Tuple[str, ...], *, strict: bool = True
    ) -> "ChangeLog":
        return cls(
            commits=tuple(
                ConventionalCommit.from_git_commit(item, strict=strict)
                for item in reversed(git_commits)
            )
        )

    @property
    def has_breaking_change(self) -> bool:
        return any(item for item in self.commits if item.is_breaking_change)

    @property
    def has_minor_change(self) -> bool:
        return len(self.feature_commits) > 0

    @property
    def has_micro_change(self) -> bool:
        return len(self.feature_commits) != len(self.commits)


def bold(value: str) -> str:
    return f"**{value}**"


def in_development_header(version: str, format_type: FormatTypeEnum) -> str:
    content = f"{version} (In Development)"
    return (
        rst_h1(content)
        if format_type == FormatTypeEnum.rst
        else markdown_h1(content)
    )


def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def markdown_h1(value: str, *, git_safe: bool = False) -> str:
    return rst_h1(value) if git_safe else markdown_header(value, level=1)


def markdown_h2(value: str, *, git_safe: bool = False) -> str:
    return rst_h2(value) if git_safe else markdown_header(value, level=2)


def markdown_h3(value: str) -> str:
    return markdown_header(value, level=3)


def markdown_header(value: str, *, level: int) -> str:
    return f'{"#" * level} {value}'


def rst_h1(value: str) -> str:
    return rst_header(value, symbol="=")


def rst_h2(value: str) -> str:
    return rst_header(value, symbol="-")


def rst_header(value: str, *, symbol: str) -> str:
    return f"{value}\n{symbol * len(value)}"


def ul_li(value: str) -> str:
    return f"- {value}"


def version_header(
    version: str,
    format_type: FormatTypeEnum,
    *,
    include_date: bool,
    is_pre_release: bool,
) -> str:
    content = version
    if include_date:
        now = datetime.datetime.utcnow()
        content = f"{version} ({now.date().isoformat()})"

    is_rst = format_type == FormatTypeEnum.rst
    functions = (
        # Release -> (Markdown, RST)
        (markdown_h1, rst_h1),
        # Pre-release -> (Markdown, RST)
        (markdown_h2, rst_h2),
    )

    return functions[int(is_pre_release)][int(is_rst)](content)
