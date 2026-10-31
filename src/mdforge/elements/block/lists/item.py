"""
Item-based list elements.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cache
from typing import Generator, Sequence

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
    __sub_items: list[ListItem] | BaseItemList | None

    def __init__(
        self,
        content: BaseElement | str,
        sub_items: Sequence[ListItemType] | BaseItemList | None = None,
    ):
        self.__element = norm_obj(content, BaseElement, CoerceSpec(coerce_text, str))
        self.__sub_items = (
            sub_items
            if sub_items is None or isinstance(sub_items, BaseItemList)
            else _norm_items(sub_items)
        )

    def _is_block(self, flavor: FlavorType) -> bool:
        """
        Check whether this list item is a block element.

        Also consider raw text which has a blank line separating multiple paragraphs.
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
        Render sub-items, if any. If given as a plain list, they're rendered in the same
        style as the parent list.
        """
        if isinstance(self.__sub_items, BaseItemList):
            yield from self.__sub_items._render_list(flavor, indent_spaces)
        elif self.__sub_items:
            yield from parent_list._render_items(
                flavor, indent_spaces, self.__sub_items, loose=False
            )


class BaseItemList(BaseBlockElement, ABC):
    """
    List containing items which can be either unordered (bulleted) or ordered
    (numbered).
    """

    __items: list[ListItem]
    """
    List of items passed from user, normalized to list items.
    """

    __loose: bool
    """
    Whether each item is wrapped in a paragraph as indicated by user.
    """

    def __init__(self, items: Sequence[ListItemType], loose: bool = False):
        """
        :param items: List items
        :param loose: If `True`, each item is formatted as a paragraph
        """
        self.__items = _norm_items(items)
        self.__loose = loose

    @abstractmethod
    def _get_marker(self, flavor: FlavorType) -> str:
        """
        Get character to indicate an item.
        """
        ...

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield from self._render_list(flavor, 0)

    def _render_list(
        self, flavor: FlavorType, indent_spaces: int
    ) -> Generator[str, None, None]:
        """
        Render this list's items at the given indentation.
        """
        yield from self._render_items(
            flavor, indent_spaces, self.__items, loose=self.__loose
        )

    def _render_items(
        self,
        flavor: FlavorType,
        indent_spaces: int,
        items: list[ListItem],
        *,
        loose: bool,
    ) -> Generator[str, None, None]:
        """
        Render the given items at the given indentation in the style of this list.
        """

        marker = self._get_marker(flavor)
        indent_str = " " * indent_spaces
        next_indent_spaces = indent_spaces + len(marker) + 1
        is_loose = loose or any(item._is_block(flavor) for item in items)

        # if there is a single item without multiple paragraphs in a list
        # specified to be loose, there would be no way for parsers to
        # determine that it's loose. wrap the item in a paragraph to ensure a
        # consistent element hierarchy.
        single_loose_item = len(items) == 1 and is_loose

        # traverse items
        for item in items:

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


class BulletList(BaseItemList):
    """
    Bullet point list.
    """

    def _get_marker(self, flavor: FlavorType) -> str:
        return "-"


class NumberedList(BaseItemList):
    """
    Numbered list.
    """

    def _get_marker(self, flavor: FlavorType) -> str:
        return "1."


def _norm_items(items: Sequence[ListItemType]) -> list[ListItem]:
    """
    Normalize items to list items.
    """
    return norm_list(items, ListItem, CoerceSpec(ListItem, (str, BaseElement)))
