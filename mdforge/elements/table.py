"""
Table element.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Literal

from ..element import BaseElement
from ..types import FlavorType

__all__ = [
    "CellType",
    "AlignType",
    "InlineTable",
    "BlockTable",
    "BaseTable",
]

type CellType = str | BaseElement | Cell
type RowType = list[CellType]
type AlignType = Literal["left", "center", "right"]


@dataclass
class Cell:

    content: str | BaseElement
    """
    Cell content.
    """

    rspan: int | None = None
    """
    Row span, only valid for `BlockTable`.
    """
    cspan: int | None = None
    """
    Column span, only valid for `BlockTable`.
    """

    @classmethod
    def _normalize(cls, cell: CellType, flavor: FlavorType) -> Cell:
        if isinstance(cell, Cell):
            return cell
        elif isinstance(cell, BaseElement):
            return Cell(cell._render_str(flavor))
        else:
            assert isinstance(cell, str)
            return Cell(cell)


@dataclass
class BaseTable(BaseElement):

    rows: list[RowType]
    """
    List of rows, each of which is a list of cells.
    """

    header: RowType | list[RowType] | None = None
    """
    Table header, which may contain multiple rows.
    """

    align: AlignType | list[AlignType] | None = None
    """
    Alignment for all columns, or a list of alignments for each column.
    """

    caption: str | None = None
    """
    Table caption.
    """

    clean: bool = False
    """
    Whether to remove top and bottom rules for this table.
    """

    def _get_rows(self, flavor: FlavorType) -> list[list[Cell]]:
        """
        Get rows, normalizing cells to `Cell` objects.
        """
        rows: list[list[Cell]] = []
        for row in self.rows:
            rows.append([Cell._normalize(cell, flavor) for cell in row])
        return rows

    def _render_row_sep(self) -> Generator[str, None, None]:
        """
        Yield lines to separate rows.
        """

    def _render_row(self, row: RowType) -> Generator[str, None, None]:
        """
        Yield lines for this row.
        """

    def _render_header(self) -> Generator[str, None, None]:
        """
        Yield lines for table header.
        """

    def _render_footer(self) -> Generator[str, None, None]:
        """
        Yield lines for table footer.
        """

    # TODO
    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        rows = self._get_rows(flavor)
        yield f"Table: {type(self).__name__}, rows: {rows}"


class InlineTable(BaseTable):
    """
    Table which only supports inline elements. Maps to a `multiline` table
    in pandoc.
    """


class BlockTable(BaseTable):
    """
    Table which supports block elements like paragraphs in addition to inline
    elements. Maps to a `grid` table in pandoc.
    """

    footer: RowType | list[RowType] | None = None
    """
    Table footer, which may contain multiple rows.
    """

    widths: list[int] | None = None
    """
    If provided, generated columns are sized to that number of characters. 
    Otherwise, widths are as small as possible.

    Useful to generate consistently-sized tables for varying content length.
    """

    # TODO
    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        rows = self._get_rows(flavor)
        yield f"Table: {type(self).__name__}, rows: {rows}"
