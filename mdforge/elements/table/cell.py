from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Iterable, Literal

from ...element import BaseElement
from ...types import FlavorType

__all__ = [
    "Cell",
    "CellType",
    "RowType",
    "AlignType",
]

type CellType = str | BaseElement | Cell
type RowType = list[CellType]
type AlignType = Literal["left", "center", "right", "default"]


VALID_ALIGNS = ["left", "center", "right", "default"]


@dataclass(frozen=True)
class Cell:

    content: str | list[str] | BaseElement
    """
    Cell content.
    """

    rspan: int | None = None
    """
    Row span, only valid for `block=True`.
    """

    cspan: int | None = None
    """
    Column span, only valid for `block=True`.
    """

    def __hash__(self):
        return id(self)

    @classmethod
    def _normalize(cls, cell: CellType) -> Cell:
        if isinstance(cell, Cell):
            return cell
        else:
            assert isinstance(cell, (str, BaseElement))
            return Cell(cell)

    @cache
    def _get_content(self, flavor: FlavorType) -> list[str]:
        """
        Get this cell's content as a list of strings.
        """
        content = self.content

        if isinstance(content, str):
            return content.split("\n")
        elif isinstance(content, Iterable):
            assert all(isinstance(line, str) for line in content)
            return list(content)

        assert isinstance(content, BaseElement)
        return list(content._render_element(flavor))
