import argparse
from pathlib import Path


def add_path_argument(parser: argparse.ArgumentParser) -> argparse.Action:
    return parser.add_argument(
        "-C",
        "--path",
        default=Path.cwd(),
        help="Directory with project. By default: current working directory",
        type=Path,
    )
