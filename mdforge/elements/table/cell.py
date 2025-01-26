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
