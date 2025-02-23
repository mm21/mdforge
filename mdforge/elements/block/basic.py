"""
Common block elements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from ...container import InlineContainerMixin
from ...element import BaseBlockElement
from ...types import FlavorType

__all__ = [
    "Heading",
    "Paragraph",
    "TextBlock",
]


@dataclass
class Heading(BaseBlockElement):
    """
    Heading, e.g. `# My heading`. If `level` not provided, it is set
    automatically based on nesting of container.
    """

    __text: str
    """
    Heading text.
    """

    __level: int | None
    """
    Heading level, or `None` to set automatically.
    """

    __heading_id: str | None
    """
    Explicit identifier.
    """

    def __init__(
        self, text: str, level: int | None = None, heading_id: str | None = None
    ):
        self.__text = text
        self.__level = level
        self.__heading_id = heading_id

    @property
    def _text(self) -> str:
        return self.__text

    @property
    def _heading_id(self) -> str | None:
        return self.__heading_id

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        level = self.__level or self._container._level

        attrs: str

        if flavor == "pandoc" and self.__heading_id:
            attrs = f" {{#{self.__heading_id}}}"
        else:
            attrs = ""

        yield f"{'#' * level} {self.__text}{attrs}"


class Paragraph(BaseBlockElement, InlineContainerMixin):

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield self._render_elements(flavor)


class TextBlock(BaseBlockElement):
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

    def _render_block(self, _: FlavorType):
        yield from self.__lines
