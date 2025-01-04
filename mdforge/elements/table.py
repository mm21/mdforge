"""
Table element.
"""

from __future__ import annotations

from typing import Generator, Literal

from ..types import FlavorType
from .element import BaseElement

__all__ = [
    "InlineTable",
    "BlockTable",
]


class BaseTable(BaseElement):

    rows: list[str | BaseElement]
    header: list[str] | None = None
    align: list[Literal["left", "center", "right"]] | None = None


class InlineTable(BaseTable):
    """
    Table which only supports inline elements.
    """

    def _render_element(self, _: FlavorType) -> Generator[str, None, None]:
        pass


class BlockTable(BaseTable):
    """
    Table which supports block elements like paragraphs in addition to inline
    elements.
    """

    def _render_element(self, _: FlavorType) -> Generator[str, None, None]:
        pass
