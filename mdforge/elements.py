"""
Exports common elements for use in document generation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Generator

from .element import BaseElement

__all__ = [
    "Heading",
    "Paragraph",
    "List",
    "ListItem",
    "ListItemType",
]

INDENT = " " * 2


type ListItemType = str | ListItem


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


@dataclass
class ListItem:
    text: str
    sub_items: list[ListItemType] = field(default_factory=list)


@dataclass
class List(BaseElement):

    items: list[ListItemType]

    def render(self) -> Generator[str, None, None]:

        def do_render(
            items: list[ListItemType], depth: int
        ) -> Generator[str, None, None]:
            for item in items:
                assert isinstance(item, str) or isinstance(item, ListItem)

                text: str
                sub_items: list[ListItemType]

                text, sub_items = (
                    (item.text, item.sub_items)
                    if isinstance(item, ListItem)
                    else (item, [])
                )

                assert isinstance(text, str)
                assert isinstance(sub_items, list)

                # render item
                yield f"{INDENT * depth}- {text}"

                # render any sub-items at next indentation depth
                yield from do_render(sub_items, depth + 1)

        yield from do_render(self.items, 0)
