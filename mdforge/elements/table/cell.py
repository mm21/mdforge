from __future__ import annotations

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

    _origin_cell: VirtualCell | None = None
    """
    Original cell from which this cell is derived, only applicable to spanned
    cells.
    """

    _lines: list[str] | None = None
    """
    Content of this cell as list of strings.
    """

    _dangling_line: str | None = None
    """
    Content line inserted in place of line separator for spanned rows.
    """

    _raw_lines: list[str] | None = None
    """
    List of raw lines, only applicable to origin cell of spanned cells.
    """

    def __init__(self, context: RenderContext, row_idx: int, col_idx: int):
        self.context = context
        self.row_idx = row_idx
        self.col_idx = col_idx

    @property
    def cell_is_set(self) -> bool:
        return self._cell is not None

    @property
    def content_is_set(self) -> bool:
        return self._lines is not None

    @property
    def is_origin(self) -> bool:
        assert self._origin_cell is not None
        return self is self._origin_cell

    @property
    def is_spanned(self) -> bool:
        return self.cell.rspan > 1 or self.cell.cspan > 1

    @property
    def cell(self) -> Cell:
        """
        Get original cell.
        """
        assert self._cell is not None
        return self._cell

    @cached_property
    def effective_width(self) -> int:
        """
        Actual width of this cell, accounting for offset due to cell spanning.
        """
        width = self.context.col_widths[self.col_idx]

        # get offset if spanning multiple cells
        span_offset = (
            len(self.context.variant.cell_sep)
            if self.cell.cspan > 1 and not self.is_last_col_span
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
    def origin_cell(self) -> VirtualCell:
        """
        Get origin virtual cell.
        """
        assert self._origin_cell is not None
        return self._origin_cell

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
        return self.col_offset == self.cell.cspan - 1

    @property
    def lines(self) -> list[str]:
        """
        Get this cell's content as list of lines, ensuring it has been set.
        """
        assert self._lines is not None
        return self._lines

    @property
    def dangling_line(self) -> str | None:
        """
        Get this cell's dangling line, if any; only applicable for cells with
        spanned rows.
        """
        return self._dangling_line

    @property
    def raw_lines(self) -> list[str]:
        assert self._raw_lines is not None
        return self._raw_lines

    def set_cell(
        self,
        cell: Cell,
        row_offset: int,
        col_offset: int,
        origin_cell: VirtualCell,
    ):
        """
        Populate with cell and any offset, if spanning multiple rows/columns.
        """
        self._cell = cell
        self._row_offset = row_offset
        self._col_offset = col_offset
        self._origin_cell = origin_cell

    def set_content(self, lines: list[str]):
        self._lines = lines

    def set_dangling_line(self, line: str):
        self._dangling_line = line

    def get_content(self) -> Generator[str, None, None]:
        """
        Get content of this cell, which may be a fragment of the original
        cell's content based on width/height offsets.
        """
        yield from self._lines
