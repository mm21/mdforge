"""
Item-based list elements.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cache
from typing import Generator

from ...._norm import CoerceSpec, norm_list, norm_obj
from ...._utils import coerce_text, wrap_para_cond
from ....element import BaseBlockElement, BaseElement
from ....types import FlavorType

__all__ = [
    "ListItemType",
    "ListItem",
    "BulletList",
    "NumberedList",
    "BaseItemList",
]


type ListItemType = BaseElement | ListItem | str


class ListItem:

    __element: BaseElement
    __sub_items: list[ListItemType] | BaseItemList | None

    def __init__(
        self,
        content: BaseElement | str,
        sub_items: list[ListItemType] | BaseItemList | None = None,
    ):
        self.__element = norm_obj(
            content, BaseElement, CoerceSpec(coerce_text, str)
        )
        self.__sub_items = sub_items

    def _is_block(self, flavor: FlavorType) -> bool:
        """
        Check whether this list item is a block element. Also consider raw
        text which has a blank line separating multiple paragraphs.
        """
        return isinstance(self.__element, BaseBlockElement) or any(
            line.strip() == "" for line in self._render_text(flavor)
        )

    @cache
    def _render_text(self, flavor: FlavorType) -> list[str]:
        """
        Get text, rendering element.
        """
        return list(self.__element._render_element_norm(flavor))

    def _render_sub_items(
        self, flavor: FlavorType, indent_spaces: int, parent_list: BaseItemList
    ) -> Generator[str, None, None]:
        """
        Render sub-items, if any.
        """
        sub_list = self.__get_sub_list(type(parent_list))

        if sub_list is None:
            return None

        yield from sub_list._render_items(flavor, indent_spaces)

    def __get_sub_list(
        self, parent_list_cls: type[BaseItemList]
    ) -> BaseItemList | None:
        """
        Get sub list from sub items, creating a new list object if items are
        given as a plain list.
        """
        if not self.__sub_items:
            return None
        elif isinstance(self.__sub_items, BaseItemList):
            return self.__sub_items
        else:
            return parent_list_cls(self.__sub_items)


class BaseItemList(BaseBlockElement, ABC):
    """
    List containing items which can be either unordered (bulleted) or ordered
    (numbered).
    """

    __items: list[ListItemType]
    """
    List of items passed from user.
    """

    __loose: bool
    """
    Whether each item is wrapped in a paragraph as indicated by user.
    """

    def __init__(self, items: list[ListItemType], loose: bool = False):
        """
        :param items: List items
        :param loose: If `True`, each item is formatted as a paragraph
        """
        self.__items = items
        self.__loose = loose

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

        items_norm = norm_list(
            self.__items if items is None else items,
            ListItem,
            CoerceSpec(ListItem, (str, BaseElement)),
        )
        marker = self._get_marker(flavor)
        indent_str = " " * indent_spaces
        next_indent_spaces = indent_spaces + len(marker) + 1
        is_loose = self.__check_loose(flavor, items_norm)

        # if there is a single item without multiple paragraphs in a list
        # specified to be loose, there would be no way for parsers to
        # determine that it's loose. wrap the item in a paragraph to ensure a
        # consistent element hierarchy.
        single_loose_item = len(items_norm) == 1 and is_loose

        # traverse items
        for item in items_norm:

            # get item text
            text: list[str] = item._render_text(flavor)
            assert len(text)

            # wrap in paragraph if needed
            if single_loose_item:
                wrap_para_cond(text)

            # render item text
            for line_idx, line in enumerate(text):

                # only apply marker to first line
                marker_ = marker if line_idx == 0 else " " * len(marker)

                yield f"{indent_str}{marker_} {line}"

            # render sub-items
            yield from item._render_sub_items(flavor, next_indent_spaces, self)

            if is_loose:
                # insert additional space between this item and next
                yield ""

        # in pandoc, inserting a comment between lists ensures they aren't
        # considered as the same list in case there is no other content
        # between them.
        # see: https://pandoc.org/MANUAL.html#ending-a-list
        yield f"{indent_str}<!-- end of list -->"

    def __check_loose(self, flavor: FlavorType, items: list[ListItem]):
        """
        Check if this list should be considered loose, either explicitly
        or based on whether there are any block items.
        """

        if self.__loose:
            return True

        if any(item._is_block(flavor) for item in items):
            return True

        return False


class BulletList(BaseItemList):
    """
    Bullet point list.
    """

    def _get_marker(self, _: FlavorType) -> str:
        return "-"


class NumberedList(BaseItemList):
    """
    Numbered list.
    """

    def _get_marker(self, _: FlavorType) -> str:
        return "1."
