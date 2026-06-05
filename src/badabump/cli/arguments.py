from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_path_argument(parser: argparse.ArgumentParser) -> argparse.Action:
    return parser.add_argument(
        "-C",
        "--path",
        default=Path.cwd(),
        help="Directory with project. By default: current working directory",
        type=Path,
    )
