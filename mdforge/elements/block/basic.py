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
    "NumberedList",
    "BulletList",
    "ListItemType",
    "ListItem",
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


class BaseList(BaseBlockElement, ABC):
    """
    List which can be either ordered or bulleted.
    """

    __items: list[ListItemType]
    """
    List of items passed from user.
    """

    def __init__(self, items: list[ListItemType]):
        self.__items = items

    @property
    @abstractmethod
    def _marker(self) -> str:
        """
        Character to indicate an item.
        """
        ...

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield from self._render_items(flavor, 0)

    def _render_items(
        self,
        flavor: FlavorType,
        indent_spaces: int,
        items: list[ListItemType] | None = None,
    ) -> Generator[str, None, None]:
        """
        Render items at the given indentation.
        """

        indent_str = " " * indent_spaces
        next_indent_spaces = indent_spaces + len(self._marker) + 1

        # normalize and traverse items
        items_norm = self.__normalize_items(
            self.__items if items is None else items
        )
        for item in items_norm:

            # render item text
            yield f"{indent_str}{self._marker} {item._get_text(flavor)}"

            # render sub-items
            if isinstance(item.sub_items, list):
                # nested items of same list type
                if len(item.sub_items):
                    yield from self._render_items(
                        flavor, next_indent_spaces, items=item.sub_items
                    )
            else:
                # nested list, may be different list type
                assert isinstance(item.sub_items, BaseList)
                yield from item.sub_items._render_items(
                    flavor, next_indent_spaces
                )

    def __normalize_items(self, items: list[ListItemType]) -> list[ListItem]:
        """
        Get items as a normalized list.
        """
        items_norm: list[ListItem] = []

        for item in items:
            if isinstance(item, (str, BaseInlineElement)):
                items_norm.append(ListItem(item))
            elif isinstance(item, ListItem):
                items_norm.append(item)
            else:
                raise ValueError(
                    f"Unexpected list item type: {item} ({type(item)})"
                )

        return items_norm


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

    def _get_text(self, flavor: FlavorType) -> str:
        """
        Get text, rendering if necessary.
        """
        if isinstance(self.text, str):
            return self.text
        else:
            assert isinstance(self.text, BaseInlineElement)
            return self.text._render_inline(flavor)
