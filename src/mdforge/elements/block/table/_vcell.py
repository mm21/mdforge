from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from ....types import AlignType
from .cell import Cell

if TYPE_CHECKING:
    from ._context import BaseRenderContext


class VirtualCell:
    """
    Cell which encapsulates a `Cell` or a spanned cell thereof. Used to
    simplify generation of cell content in that virtual cells have
    consistent column counts.
    """

    context: BaseRenderContext
    """
    Render context.
    """

    row_idx: int
    """
    Row index in table.
    """

    col_idx: int
    """
    Column index in table.
    """

    __cell: Cell | None = None
    """
    Original cell, which may span multiple rows/columns.
    """

    __col_offset: int | None = None
    """
    Column offset from the original cell.
    """

    __origin_vcell: VirtualCell | None = None
    """
    Original cell from which this cell is derived, only applicable to spanned
    cells.
    """

    __lines: list[str] | None = None
    """
    Content of this cell as list of strings.
    """

    __dangling_line: str | None = None
    """
    Content line inserted in place of line separator for spanned rows.
    """

    def __init__(self, context: BaseRenderContext, row_idx: int, col_idx: int):
        self.context = context
        self.row_idx = row_idx
        self.col_idx = col_idx

    @property
    def cell_is_set(self) -> bool:
        return self.__cell is not None

    @property
    def content_is_set(self) -> bool:
        return self.__lines is not None

    @property
    def is_origin(self) -> bool:
        assert self.__origin_vcell is not None
        return self is self.__origin_vcell

    @property
    def is_spanned(self) -> bool:
        return self.cell._rspan > 1 or self.cell._cspan > 1

    @property
    def cell(self) -> Cell:
        """
        Get origin cell.
        """
        assert self.__cell is not None
        return self.__cell

    @cached_property
    def effective_width(self) -> int:
        """
        Actual width of this cell, accounting for offset due to cell spanning.
        """
        width = self.context.col_widths[self.col_idx]

        # get offset if spanning multiple cells
        span_offset = (
            len(self.context.variant.cell_sep)
            if self.cell._cspan > 1 and not self.is_last_col_span
            else 0
        )
        return width + span_offset

    @property
    def align(self) -> AlignType:
        """
        Get alignment of this cell.
        """
        return self.context.params.col_aligns[self.col_idx]

    @property
    def col_offset(self) -> int:
        """
        Get column offset from the original cell.
        """
        assert self.__col_offset is not None
        return self.__col_offset

    @property
    def is_last_col(self) -> bool:
        """
        Whether this is the last column in the row.
        """
        return self.col_idx == self.context.params.col_count - 1

    @property
    def is_last_col_span(self) -> bool:
        """
        Whether this is the last spanned column.
        """
        return self.col_offset == self.cell._cspan - 1

    @property
    def lines(self) -> list[str]:
        """
        Get this cell's content as list of lines, ensuring it has been set.
        If cell spans multiple rows/columns, this is a fragment of the content
        in the origin cell.
        """
        assert self.__lines is not None
        return self.__lines

    @property
    def dangling_line(self) -> str | None:
        """
        Get this cell's dangling line, if any; only applicable for cells with
        spanned rows.
        """
        return self.__dangling_line

    def set_cell(
        self,
        cell: Cell,
        col_offset: int,
        origin_vcell: VirtualCell,
    ):
        """
        Populate with cell and any offset, if spanning multiple rows/columns.
        """
        self.__cell = cell
        self.__col_offset = col_offset
        self.__origin_vcell = origin_vcell

    def set_lines(self, lines: list[str]):
        """
        Set content for this cell.
        """
        self.__lines = lines

    def set_dangling_line(self, line: str):
        """
        Set cell content line to occupy a segment of a separator line. Only
        applicable to cells which span multiple rows.
        """
        self.__dangling_line = line
