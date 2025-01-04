"""
Table element.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Literal

from ..element import BaseElement
from ..types import FlavorType

__all__ = [
    "InlineTable",
    "BlockTable",
    "AlignT",
]

type AlignT = Literal["left", "center", "right"]


@dataclass
class BaseTable(BaseElement):

    rows: list[list[str | BaseElement]]
    header: list[str] | None = None
    align: AlignT | list[AlignT] | None = None

    def _get_rows(self, flavor: FlavorType) -> list[str]:
        """
        Render any rows containing elements.
        """

        rows: list[list[str]] = []

        for row in self.rows:
            row_new = []
            for cell in row:
                if isinstance(cell, BaseElement):
                    row_new.append("\n".join(cell._render_element(flavor)))
                else:
                    assert isinstance(cell, str)
                    row_new.append(cell)
            rows.append(row_new)
        return rows


class InlineTable(BaseTable):
    """
    Table which only supports inline elements.
    """

    # TODO
    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        rows = self._get_rows(flavor)
        yield f"Table: {self}, rows: {rows}"


class BlockTable(BaseTable):
    """
    Table which supports block elements like paragraphs in addition to inline
    elements.
    """

    # TODO
    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        rows = self._get_rows(flavor)
        yield f"Table: {self}, rows: {rows}"
