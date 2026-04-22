"""
Text-based block elements.
"""

from __future__ import annotations

from typing import Generator

from ...container import InlineContainerMixin
from ...element import BaseBlockElement
from ...types import FlavorType

__all__ = [
    "Paragraph",
    "BlockText",
]


class Paragraph(InlineContainerMixin, BaseBlockElement):

    _allow_multiline = True

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield self._render_elements(flavor)


class BlockText(BaseBlockElement):
    """
    Block element containing a single string, which may have multiple lines.
    """

    __lines: list[str]

    def __init__(self, text: str):
        self.__lines = text.strip().split("\n")

    @property
    def _has_empty_lines(self) -> bool:
        """
        Check if text block has any empty lines.
        """
        return any(line.strip() == "" for line in self.__lines)

    def _render_block(self, _: FlavorType) -> Generator[str, None, None]:
        yield from self.__lines
