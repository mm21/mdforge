"""
Common block elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generator

from ..._containers import BaseInlineElementContainerMixin
from ...element import BaseBlockElement
from ...types import FlavorType

__all__ = [
    "Heading",
    "Paragraph",
    "BulletList",
    "ListItem",
    "ListItemType",
]

INDENT = " " * 2


type ListItemType = str | ListItem


@dataclass
class Heading(BaseBlockElement):
    """
    Heading, e.g. `# My heading`. If `level` not provided, it is set
    automatically based on nesting of container.
    """

    text: str
    """
    Heading text.
    """

    level: int | None = None
    """
    Heading level, or `None` to set automatically.
    """

    def _render_block(self, _: FlavorType) -> Generator[str, None, None]:
        level = self.level or self._container._level
        yield f"{'#' * level} {self.text}"


class Paragraph(BaseBlockElement, BaseInlineElementContainerMixin):

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield self._render_elements(flavor)


@dataclass
class ListItem:
    text: str

    # TODO: support nested lists, e.g. numbered list in bullet list
    sub_items: list[ListItemType] = field(default_factory=list)


@dataclass
class BulletList(BaseBlockElement):

    items: list[ListItemType]

    def _render_block(self, _: FlavorType) -> Generator[str, None, None]:

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
