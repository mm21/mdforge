"""
Encapsulates latex commands to tune tables by optionally omitting top and
bottom rules.
"""

from __future__ import annotations

from typing import Generator

CLEAN_COMMANDS = [
    "toprule",
    "bottomrule",
    "endfoot",
    "endlastfoot",
]
"""
List of commands to save/restore for clean tables.
"""


def get_clean_start() -> Generator[str, None, None]:
    for cmd in CLEAN_COMMANDS:
        yield rf"\let\old{cmd}\{cmd}"
        yield rf"\renewcommand{{\{cmd}}}{{}}"


def get_clean_end() -> Generator[str, None, None]:
    for cmd in CLEAN_COMMANDS:
        yield rf"\let\{cmd}\old{cmd}"
