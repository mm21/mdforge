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

    coords: tuple[int, int]
    """
    Coordinates of this cell as (row index, col index).
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

    def __init__(self, context: RenderContext, coords: tuple[int, int]):
        self.context = context
        self.coords = coords

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

    def set(self, cell: Cell, row_offset: int, col_offset: int):
        """
        Populate with cell and any offset, if spanning multiple rows/columns.
        """
        self._cell = cell
        self._row_offset = row_offset
        self._col_offset = col_offset

    def get_content(
        self, width: int | None = None
    ) -> Generator[str, None, None]:
        """
        Get content of this cell, which may be a fragment of the orignal
        cell's content based on width/height offsets.
        """

        # TODO: get width/height offset based on widths of preceding rows/cols

        if self.row_offset == 0 and self.col_offset == 0:
            yield from self.cell._get_content(self.context.flavor, width=width)
        else:
            yield ""
