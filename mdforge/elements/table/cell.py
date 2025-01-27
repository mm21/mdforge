from __future__ import annotations

from dataclasses import dataclass
from functools import cache
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
        content: list[str]

        if isinstance(raw_content, str):
            content = raw_content.split("\n")
        elif isinstance(raw_content, Iterable):
            assert all(isinstance(line, str) for line in raw_content)
            content = list(raw_content)
        else:
            assert isinstance(raw_content, BaseElement)
            content = list(raw_content._render_element(flavor))

        if width:
            # wrap words
            wrapped_content: list[str] = []

            for line in content:
                if len(line) <= width:
                    # already within required width
                    wrapped_content.append(line)
                else:
                    # split line into words
                    words = line.split()
                    line_new = ""

                    for word in words:
                        if len(line_new) + len(word) + 1 <= width:
                            # word fits in current line
                            space = " " if len(line_new) else ""
                            line_new += f"{space}{word}"
                        else:
                            # word doesn't fit in current line
                            assert (
                                len(word) <= width
                            ), f"Unable to wrap line: len({word})={len(word)} > {width}"
                            wrapped_content.append(line_new)
                            line_new = word

                    # done processing words, add last line if not empty
                    if len(line_new):
                        wrapped_content.append(line_new)

            return wrapped_content
        else:
            return content


class WrappedCell:
    """
    Cell which wraps a `Cell`, representing any spanned cells.
    """

    context: RenderContext
    """
    Render context.
    """

    row_idx: int
    """
    Row index.
    """

    col_idx: int
    """
    Column index.
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
        width: int | None = None,
        align: AlignType | None = None,
        align_space: bool = False,
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
                self.cell._get_content(self.context.flavor, width=width)
            )
        else:
            raw_lines = [""]

        for raw_line in raw_lines:
            yield self.format_line(
                raw_line, width=width, align=align, align_space=align_space
            )

    def format_line(
        self,
        raw_line: str,
        width: int | None = None,
        align: AlignType | None = None,
        align_space: bool = False,
    ) -> str:
        """
        Take raw content line and format based on table configuration.
        """

        if width:
            # align and pad to width
            leading_str, trailing_str = self._leading_str, self._trailing_str
            effective_width = width + self._width_offset_sep

            align_char = self._get_align_char(align, align_space)
            padded_line = f"{raw_line:{align_char}{effective_width}}"

            return f"{leading_str}{padded_line}{trailing_str}"
        else:
            return raw_line

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
        return self.col_idx == self.context.col_count - 1

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

    def _get_align_char(self, align: AlignType | None, align_space: bool):
        match align if align_space else None:
            case "center":
                return "^"
            case "right":
                return ">"
            case _:
                return "<"
