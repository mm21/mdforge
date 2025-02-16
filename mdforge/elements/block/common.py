"""
Common block elements.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator

from ..._containers import InlineElementContainerMixin
from ...element import BaseBlockElement, BaseInlineElement
from ...types import FlavorType

__all__ = [
    "Heading",
    "Paragraph",
    "BaseList",
    "NumberedList",
    "BulletList",
    "ListItem",
    "ListItemType",
]


type ListItemType = str | BaseInlineElement | ListItem


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


class Paragraph(BaseBlockElement, InlineElementContainerMixin):

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield self._render_elements(flavor)


@dataclass
class BaseList(BaseBlockElement, ABC):
    """
    List which can be either ordered or bulleted.
    """

    items: list[ListItemType]

    @property
    @abstractmethod
    def _marker(self) -> str:
        """
        Character to indicate an item.
        """
        ...

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:

        def do_render(
            items: list[ListItemType], depth: int, marker: str
        ) -> Generator[str, None, None]:

            indent_spaces = len(marker) + 1
            next_depth = indent_spaces + depth

            for item in items:

                text: str
                sub_items: list[ListItemType]

                next_marker = marker

                if isinstance(item, str):
                    text, sub_items = item, []
                elif isinstance(item, BaseInlineElement):
                    text, sub_items = item._render_inline(flavor), []
                elif isinstance(item, ListItem):
                    raw_text, raw_sub_items = item.text, item.sub_items

                    # handle inline element as text
                    if isinstance(raw_text, BaseInlineElement):
                        text = raw_text._render_inline(flavor)
                    else:
                        text = raw_text

                    # handle nested list as sub items
                    if isinstance(raw_sub_items, BaseList):
                        next_marker = raw_sub_items._marker
                        sub_items = raw_sub_items.items
                    else:
                        sub_items = raw_sub_items
                else:
                    raise ValueError(
                        f"Unexpected list item type: {item} ({type(item)})"
                    )

                assert isinstance(text, str)
                assert isinstance(sub_items, list)

                # render item text
                yield f"{' ' * depth}{marker} {text}"

                # render any sub-items at next indentation depth
                yield from do_render(sub_items, next_depth, next_marker)

        yield from do_render(self.items, 0, self._marker)


class NumberedList(BaseList):
    """
    Numbered list.
    """

    @property
    def _marker(self) -> str:
        return "1."


class BulletList(BaseList):
    """
    Bullet point list.
    """

    @property
    def _marker(self) -> str:
        return "-"


@dataclass
class ListItem:
    text: str | BaseInlineElement
    sub_items: list[ListItemType] | BaseList = field(default_factory=list)
