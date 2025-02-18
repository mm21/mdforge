"""
List elements.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generator

from ...element import BaseBlockElement, BaseElement
from ...types import FlavorType

__all__ = [
    "ListItemType",
    "ListItem",
    "BulletList",
    "NumberedList",
    "BaseList",
]


type ListItemType = str | BaseElement | ListItem


class ListItem:
    __text: str | BaseElement
    __sub_items: list[ListItemType] | BaseList | None

    def __init__(
        self,
        text: str | BaseElement,
        sub_items: list[ListItemType] | BaseList | None = None,
    ):
        self.__text = text
        self.__sub_items = sub_items

    @property
    def _is_block(self) -> bool:
        return isinstance(self.__text, BaseBlockElement)

    def _render_text(self, flavor: FlavorType) -> Generator[str, None, None]:
        """
        Get text, rendering if necessary.
        """
        text: str

        if isinstance(self.__text, str):
            text = self.__text
        else:
            assert isinstance(self.__text, BaseElement)
            # join first, then split later in case any elements have newlines
            # embedded
            text = "\n".join(self.__text._render_element(flavor))

        yield from text.split("\n")

    def _render_sub_items(
        self, flavor: FlavorType, indent_spaces: int, parent_list: BaseList
    ) -> Generator[str, None, None]:
        """
        Render sub-items, if any.
        """
        sub_list = self.__get_sub_list(type(parent_list))

        if sub_list is None:
            return None

        yield from sub_list._render_items(flavor, indent_spaces)

    def __get_sub_list(
        self, parent_list_cls: type[BaseList]
    ) -> BaseList | None:
        """
        Get sub list from sub items.
        """
        if not self.__sub_items:
            return None
        elif isinstance(self.__sub_items, BaseList):
            return self.__sub_items
        else:
            return parent_list_cls(self.__sub_items)


class BaseList(BaseBlockElement, ABC):
    """
    List which can be either bulleted or ordered.
    """

    __items: list[ListItemType]
    """
    List of items passed from user.
    """

    __loose: bool
    """
    Whether each item is wrapped in a paragraph, either as indicated by user
    or inferred by one of the items having block content.
    """

    def __init__(self, items: list[ListItemType], loose: bool = False):
        """
        :param items: List items
        :param loose: If `True`, each item is formatted as a paragraph
        """
        self.__items = items
        self.__loose = loose or self.__check_loose(items)

    @abstractmethod
    def _get_marker(self, flavor: FlavorType) -> str:
        """
        Get character to indicate an item.
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

        marker = self._get_marker(flavor)
        indent_str = " " * indent_spaces
        next_indent_spaces = indent_spaces + len(marker) + 1
        desc = f"{type(self).__name__}(loose={self.__loose})"

        # in pandoc, inserting a comment between lists ensures they aren't
        # considered as the same list in case there is no other content
        # between them. might as well add a start comment too.
        # see: https://pandoc.org/MANUAL.html#ending-a-list
        yield f"{indent_str}<!-- start: {desc} -->"

        # normalize items
        items_norm = self.__normalize_items(
            self.__items if items is None else items
        )

        # if there is a single item in a list specified to be loose,
        # there would be no way for parsers to determine that it's loose.
        # wrap the item in a paragraph for consistent element hierarchy.
        single_loose_item = len(items_norm) == 1 and self.__loose

        # traverse items
        for item in items_norm:

            # get item text
            text: list[str] = list(item._render_text(flavor))
            assert len(text) >= 1

            # wrap in paragraph if needed
            if single_loose_item:
                text[0] = f"<p>{text[0]}"
                text[-1] = f"{text[-1]}</p>"

            # render item text
            for line_idx, line in enumerate(text):

                # only apply marker to first line
                marker_ = marker if line_idx == 0 else " " * len(marker)

                yield f"{indent_str}{marker_} {line}"

            # render sub-items
            yield from item._render_sub_items(flavor, next_indent_spaces, self)

            if self.__loose:
                # insert additional space between this item and next
                yield ""

        yield f"{indent_str}<!-- end: {desc} -->"

    def __check_loose(self, items: list[ListItemType]):
        """
        Check if there are any non-list block elements in items. If so,
        consider this a loose list so blank lines are inserted between
        elements.

        Otherwise, the list would not be considered loose if the last item
        was a block element.
        """

        for item in items:
            if isinstance(item, BaseBlockElement):
                return True
            elif isinstance(item, ListItem) and item._is_block:
                return True

        return False

    def __normalize_items(self, items: list[ListItemType]) -> list[ListItem]:
        """
        Get items as a normalized list.
        """
        items_norm: list[ListItem] = []

        for item in items:
            if isinstance(item, (str, BaseElement)):
                items_norm.append(ListItem(item))
            elif isinstance(item, ListItem):
                items_norm.append(item)
            else:
                raise ValueError(
                    f"Unexpected list item type: {item} ({type(item)})"
                )

        return items_norm


class BulletList(BaseList):
    """
    Bullet point list.
    """

    def _get_marker(self, _: FlavorType) -> str:
        return "-"


class NumberedList(BaseList):
    """
    Numbered list.
    """

    def _get_marker(self, flavor: FlavorType) -> str:
        if flavor == "pandoc":
            # with fancy_lists extension
            return "#."
        else:
            return "1."
