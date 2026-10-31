"""
Block elements which wrap other block elements.
"""

from __future__ import annotations

from typing import Generator

from ...container import BaseBlockContainer
from ...element import BaseElement, RenderContext
from ...exceptions import ValidationError
from ...types import AlignType

__all__ = [
    "Quote",
    "AlignedBlock",
]

VALID_BLOCK_ALIGNS = ["left", "center", "right"]


class Quote(BaseBlockContainer):
    """
    Block quote containing one or more block elements.
    """

    def __init__(self, *elements: BaseElement | str):
        super().__init__()
        self += elements

    def _render_block(self, context: RenderContext) -> Generator[str, None, None]:
        for line in "\n".join(super()._render_block(context)).split("\n"):
            yield f"> {line}" if line else ">"


class AlignedBlock(BaseBlockContainer):
    """
    Block containing one or more block elements with the given alignment, wrapped in
    HTML: `<center>` if centered, which also centers nested blocks like tables, or a
    `<div>` with `text-align` otherwise.
    """

    __align: AlignType

    def __init__(self, *elements: BaseElement | str, align: AlignType = "center"):
        """
        :param elements: Elements to add
        :param align: Alignment, one of `left`, `center`, or `right`
        """
        if align not in VALID_BLOCK_ALIGNS:
            raise ValidationError(f"Invalid block alignment: {align}")

        super().__init__()
        self.__align = align
        self += elements

    def _render_block(self, context: RenderContext) -> Generator[str, None, None]:
        if self.__align == "center":
            start, end = "<center>", "</center>"
        else:
            start, end = f'<div style="text-align: {self.__align};">', "</div>"

        # blank lines are required for content to be parsed as markdown
        yield start
        yield ""
        yield from super()._render_block(context)
        yield ""
        yield end
