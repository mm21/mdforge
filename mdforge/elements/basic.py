"""
Basic Markdown elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generator

from ..types import FlavorType
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

    text: str
    """
    Heading text.
    """

    level: int | None = None
    """
    Heading level, or `None` to set automatically based on nesting of 
    container.
    """

    def _render_element(self, _: FlavorType) -> Generator[str, None, None]:
        level = self.level or self._container._level
        yield f"{'#' * level} {self.text}"


@dataclass
class Paragraph(BaseElement):

    lines: str | list[str]

    def _render_element(self, _: FlavorType) -> Generator[str, None, None]:
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

    def _render_element(self, _: FlavorType) -> Generator[str, None, None]:

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
