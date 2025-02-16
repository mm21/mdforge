from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, Iterable, Literal

from ....element import BaseBlockElement, BaseElement
from ....types import FlavorType

if TYPE_CHECKING:
    pass

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
    Represents a table cell which can span multiple rows/columns, if the given
    flavor supports it.
    """

    content: str | list[str] | BaseElement
    """
    Cell content, consisting of one or more lines or an element.
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
            # TODO: handle inline vs block
            assert isinstance(raw_content, BaseBlockElement)
            lines = list(raw_content._render_block(flavor))

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
