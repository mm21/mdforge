"""
Definition list.
"""

from __future__ import annotations

from typing import Generator, Iterable

from ....element import BaseBlockElement, BaseElement, BaseInlineElement
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
        term: str | BaseInlineElement,
        definitions: str | BaseElement | list[str | BaseElement],
    ):
        """
        :param term: Term, must be an inline element
        :param definitions: List of elements corresponding to term; may be inline or block elements, but compact definition lists require that all definitions be inline only
        """

        def normalize_defs(
            defs: str | BaseElement | list[str | BaseElement],
        ) -> list[BaseElement]:

            # normalize to list of strings or elements
            defs_: list[str | BaseElement] = (
                [defs]
                if not isinstance(defs, Iterable) or isinstance(defs, str)
                else defs
            )

            defs_norm: list[BaseElement] = []

            # normalize to list of elements
            for d in defs_:
                if isinstance(d, str):
                    defs_norm.append(Text(d))
                elif isinstance(d, BaseElement):
                    defs_norm.append(d)
                else:
                    raise ValueError(
                        f"Definition must be str or BaseElement: {d}"
                    )

            return defs_norm

        term_ = Text(term) if isinstance(term, str) else term
        definitions_ = normalize_defs(definitions)

        if not isinstance(term_, BaseInlineElement):
            raise ValueError(
                f"Term must be an inline element: {term_} ({type(term_)})"
            )

        self.__term = term_
        self.__definitions = definitions_

    def _validate(self, compact: bool):
        if compact:
            for definition in self.__definitions:
                if not isinstance(definition, BaseInlineElement):
                    raise ValueError(
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
            for line_idx, line in enumerate(definition._render_element(flavor)):

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

    def __init__(self, items: list[DefinitionItem], compact: bool = False):
        """
        :param items: List of definition items
        :param compact: Whether to generate a compact list, with no paragraph wrapping the definitions; if `True`, all definitions must be inline elements
        """

        for item in items:
            item._validate(compact)

        self.__items = items
        self.__compact = compact

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:

        for item_idx, item in enumerate(self.__items):

            is_last_item = item_idx == len(self.__items)

            # render this item
            yield from item._render(flavor, self.__compact)

            # render blank line between items
            if not is_last_item:
                yield ""
