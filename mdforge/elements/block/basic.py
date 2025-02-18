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
]


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


class Paragraph(BaseBlockElement, InlineContainerMixin):

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield self._render_elements(flavor)
