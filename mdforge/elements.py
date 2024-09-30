"""
Exports common elements for use in document generation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Generator

from ._element import BaseElement

__all__ = [
    "Heading",
    "Paragraph",
    "List",
]

INDENT = " " * 2


@dataclass
class Heading(BaseElement):
    """
    Heading, e.g. `# My heading`.
    """

    title: str
    level: int = 1

    def render(self) -> Generator[str, None, None]:
        yield f"{'#' * self.level} {self.title}"


@dataclass
class Paragraph(BaseElement):

    lines: str | list[str]

    def render(self) -> Generator[str, None, None]:
        lines = [self.lines] if isinstance(self.lines, str) else self.lines
        assert all(isinstance(l, str) for l in lines)

        yield from lines


type ListItemType = str | list[ListItemType]


@dataclass
class List(BaseElement):

    items: list[ListItemType]

    def render(self) -> Generator[str, None, None]:

        def do_render(
            items: list[ListItemType], depth: int
        ) -> Generator[str, None, None]:
            for item in items:
                if isinstance(item, str):
                    yield f"{INDENT * depth}- {item}"
                else:
                    assert isinstance(item, list)
                    yield from do_render(item, depth + 1)

        yield from do_render(self.items, 0)
