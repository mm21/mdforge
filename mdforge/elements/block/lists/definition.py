"""
Definition list.
"""

from __future__ import annotations

from typing import Generator, Iterable

from ...._norm import CoerceSpec, norm_list, norm_obj
from ....element import BaseBlockElement, BaseElement, BaseInlineElement
from ....exceptions import ValidationError
from ....types import FlavorType
from ...inline.text import Text

__all__ = [
    "DefinitionItem",
    "DefinitionList",
]

INDENT = 4


class DefinitionItem:
    """
    A definition entry in a definition list, consisting of a term and one
    or more definitions.
    """

    __term: BaseInlineElement
    __definitions: list[BaseElement]

    def __init__(
        self,
        term: BaseInlineElement | str,
        definitions: BaseElement | str | list[BaseElement | str],
    ):
        """
        :param term: Term as a string or inline element
        :param definitions: One or more definitions; may be inline or block elements, but compact definition lists require that all definitions be inline only
        """
        self.__term = norm_obj(term, BaseInlineElement, CoerceSpec(Text, str))
        self.__definitions = norm_list(
            definitions, BaseElement, CoerceSpec(Text, str)
        )

    def _validate(self, compact: bool):
        if compact:
            for definition in self.__definitions:
                if not isinstance(definition, BaseInlineElement):
                    raise ValidationError(
                        f"Definition must be inline element for compact definition list: {definition} ({type(definition)})"
                    )

    def _render(
        self, flavor: FlavorType, compact: bool
    ) -> Generator[str, None, None]:

        # term goes on line by itself
        yield self.__term._render_inline(flavor)

        if not compact:
            # insert blank line for non-compact list
            yield ""

        # render definitions
        for def_idx, definition in enumerate(self.__definitions):
            is_last_def = def_idx == len(self.__definitions) - 1

            # render lines for this definition
            for line_idx, line in enumerate(
                definition._render_element_norm(flavor)
            ):

                # include ":" for first line
                is_first_line = line_idx == 0
                leading_char, indent = (
                    (":", INDENT - 1) if is_first_line else ("", INDENT)
                )

                yield f"{leading_char}{' '*indent}{line}"

            # render blank line between definitions if required
            if not (is_last_def or compact):
                yield ""


class DefinitionList(BaseBlockElement):
    """
    Definition list element.
    """

    __items: list[DefinitionItem]
    __compact: bool

    def __init__(
        self,
        items: DefinitionItem | Iterable[DefinitionItem],
        compact: bool = False,
    ):
        """
        :param items: One or more definition items
        :param compact: Whether to generate a compact list, with no paragraph wrapping the definitions; if `True`, all definitions must be inline elements
        """

        items_norm = norm_list(items, DefinitionItem)

        for item in items_norm:
            item._validate(compact)

        self.__items = items_norm
        self.__compact = compact

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:

        for item_idx, item in enumerate(self.__items):
            is_last_item = item_idx == len(self.__items)

            # render this item
            yield from item._render(flavor, self.__compact)

            # render blank line between items
            if not is_last_item:
                yield ""

        # in case of back-to-back definition lists with no elements in between,
        # add a comment so they don't get considered as the same list
        yield "<!-- end of definition list -->"

    def _get_pandoc_extensions(self) -> set[str]:
        return {"definition_lists"} | super()._get_pandoc_extensions()
