from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cache, cached_property
from typing import TYPE_CHECKING, Generator, Iterable, Literal

from ...element import BaseElement
from ...types import FlavorType

if TYPE_CHECKING:
    from ._context import RenderContext

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
    """
    Represents a table cell which can span multiple rows/columns.
    """

    content: str | list[str] | BaseElement
    """
    Cell content.
    """

    rspan: int = 1
    """
    Row span, can only be greater than 1 for tables with `block=True`.
    """

    cspan: int = 1
    """
    Column span, can only be greater than 1 for tables with `block=True`.
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
    def _get_content(
        self, flavor: FlavorType, width: int | None = None
    ) -> list[str]:
        """
        Get this cell's content as a list of strings, wrapping words if
        width provided.
        """

        raw_content = self.content
        lines: list[str]

        # normalize into list of lines
        if isinstance(raw_content, str):
            lines = raw_content.split("\n")
        elif isinstance(raw_content, Iterable):
            assert all(isinstance(line, str) for line in raw_content)
            lines = list(raw_content)
        else:
            assert isinstance(raw_content, BaseElement)
            lines = list(raw_content._render_element(flavor))

        if width:
            # wrap words
            wrapped_lines: list[str] = []

            for line in lines:
                wrapped_lines += self._wrap_line(line, width)

            return wrapped_lines
        else:
            return lines

    def _wrap_line(self, line: str, width: int) -> list[str]:
        """
        Wrap the provided line if necessary and return a list of resulting
        lines.
        """

        if len(line) <= width:
            # already within required width
            return [line]

        # not within required width, need to wrap
        lines: list[str] = []

        # split line into words
        words = line.split()
        line_new = ""

        for word in words:
            offset = 1 if len(line_new) else 0
            if len(line_new) + len(word) + offset <= width:
                # word fits in current line, with a space in between
                # if the current line is empty
                space = " " if len(line_new) else ""
                line_new += f"{space}{word}"
            else:
                # word doesn't fit in current line, append current line
                # and start new one
                assert (
                    len(word) <= width
                ), f"Unable to wrap line: len({word})={len(word)} > {width}"
                lines.append(line_new)
                line_new = word

        # done processing words, add last line if not empty
        if len(line_new):
            lines.append(line_new)

        return lines

    def _get_raw_width(self, flavor: FlavorType) -> int:
        """
        Get width of this cell with no wrapping or explicit width from user.
        """
        return max(len(line) for line in self._get_content(flavor))


class VirtualCell:
    """
    Cell which encapsulates a `Cell` or a spanned cell thereof.
    """

    context: RenderContext
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

    _cell: Cell | None = None
    """
    Original cell, which may span multiple rows/columns.
    """

    _row_offset: int | None = None
    """
    Row offset from the original cell.
    """

    _col_offset: int | None = None
    """
    Column offset from the original cell.
    """

    def __init__(self, context: RenderContext, row_idx: int, col_idx: int):
        self.context = context
        self.row_idx = row_idx
        self.col_idx = col_idx

    @property
    def is_set(self) -> bool:
        return self._cell is not None

    @property
    def cell(self) -> Cell:
        """
        Get original cell.
        """
        assert self._cell is not None
        return self._cell

    @cached_property
    def raw_width(self) -> int:
        """
        Width of this cell with no wrapping or explicit width from user,
        handling any column spanning.
        """

        # get raw width of original cell
        cell_width = self.cell._get_raw_width(self.context.flavor)

        # get padding between cells
        # TODO: use self.context.variant.cell_sep after refactor
        cell_sep = self.context.variant.cell_sep or " "
        padding_width = (self.cell.cspan - 1) * len(cell_sep)

        # get effective total width
        total_width = max(cell_width - padding_width, cell_width)

        # divide width amongst all the columns spanned
        width_div = math.ceil(total_width / self.cell.cspan)

        if not self._is_last_col_span:
            # not the last spanned column, this should be its width
            return width_div
        else:
            # the last spanned column, so it may be unnecessarily long - just
            # use the remaining width
            current_width = width_div * (self.cell.cspan - 1)
            return cell_width - current_width

    @cached_property
    def final_width(self) -> int:
        """
        Width of this cell, accounting for any explicit widths from user.
        """
        return self.context.col_widths[self.col_idx]

    @property
    def align(self) -> AlignType:
        """
        Get alignment of this cell.
        """
        return self.context.params.col_aligns[self.col_idx]

    @property
    def row_offset(self) -> int:
        """
        Get row offset from the original cell.
        """
        assert self._row_offset is not None
        return self._row_offset

    @property
    def col_offset(self) -> int:
        """
        Get column offset from the original cell.
        """
        assert self._col_offset is not None
        return self._col_offset

    @property
    def width_offset(self) -> int:
        """
        Get total additional width offset.
        """
        return (
            len(self._leading_str)
            + len(self._trailing_str)
            + self._width_offset_sep
        )

    def set_cell(self, cell: Cell, row_offset: int, col_offset: int):
        """
        Populate with cell and any offset, if spanning multiple rows/columns.
        """
        self._cell = cell
        self._row_offset = row_offset
        self._col_offset = col_offset

    def get_content(
        self,
    ) -> Generator[str, None, None]:
        """
        Get content of this cell, which may be a fragment of the orignal
        cell's content based on width/height offsets.
        """

        # get full content
        # TODO:
        # - get width/height offset, size based on widths of preceding rows/cols
        # - trim content based on offsets, size
        if self.row_offset == 0 and self.col_offset == 0:
            raw_lines = list(
                self.cell._get_content(
                    self.context.flavor, width=self.final_width
                )
            )
        else:
            raw_lines = [""]

        for raw_line in raw_lines:
            yield self.format_line(raw_line)

    def format_line(
        self,
        raw_line: str,
    ) -> str:
        """
        Take raw content line and format based on table configuration.
        """
        # align and pad to width
        leading_str, trailing_str = self._leading_str, self._trailing_str
        effective_width = self.final_width + self._width_offset_sep

        align_char = self._get_align_char()
        padded_line = f"{raw_line:{align_char}{effective_width}}"

        return f"{leading_str}{padded_line}{trailing_str}"

    @property
    def _cell_sep(self) -> str | None:
        return self.context.variant.cell_sep

    @property
    def _width_offset_sep(self) -> int:
        """
        Get additional width offset due to separator.
        """
        return 2 if self._cell_sep is None else 0

    @property
    def _is_first_col(self) -> bool:
        return self.col_idx == 0

    @property
    def _is_last_col(self) -> bool:
        return self.col_idx == self.context.params.col_count - 1

    @property
    def _is_first_col_span(self) -> bool:
        return self.col_offset == 0

    @property
    def _is_last_col_span(self) -> bool:
        return self.col_offset == self.cell.cspan - 1

    @property
    def _leading_str(self) -> str:
        if self._is_first_col:
            return f"{self._cell_sep} " if self._cell_sep else ""
        elif self._is_first_col_span:
            return " " if self._cell_sep else ""
        else:
            return ""

    @property
    def _trailing_str(self) -> str:
        if self._is_last_col:
            return f" {self._cell_sep}" if self._cell_sep else ""
        elif self._is_last_col_span:
            return f" {self._cell_sep}" if self._cell_sep else " "
        else:
            return ""

    def _get_align_char(self):
        match self.align if self.context.variant.align_space else "left":
            case "center":
                return "^"
            case "right":
                return ">"
            case _:
                return "<"
