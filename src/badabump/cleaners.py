import re
from typing import List


CO_AUTHORED_BY = "Co-authored-by: "
COMMIT_SUBJECT_WITH_PR_RE = re.compile(r"^(?P<subject>.+) \(\#\d+\)$")
SIGNED_OFF_BY = "Signed-off-by: "


def clean_body(body: List[str]) -> str:
    cleaned = "\n".join(
        item
        for item in body
        if not item.startswith((CO_AUTHORED_BY, SIGNED_OFF_BY))
    )
    if cleaned[-1:] == "\n":
        return cleaned
    return f"{cleaned}\n"


def clean_commit_subject(value: str) -> str:
    return COMMIT_SUBJECT_WITH_PR_RE.sub(r"\1", value)


def clean_tag_ref(value: str) -> str:
    if value[:10] == "refs/tags/":
        return value[10:]
    return value
