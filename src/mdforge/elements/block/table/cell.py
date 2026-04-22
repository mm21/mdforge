from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Iterable

from ...._norm import CoerceSpec, norm_obj
from ...._utils import coerce_text, wrap_para_cond
from ....element import BaseElement, BaseInlineElement
from ....exceptions import RenderError
from ....types import FlavorType
from ..text import BlockText

if TYPE_CHECKING:
    pass

__all__ = [
    "Cell",
    "CellType",
    "RowType",
]

type CellType = BaseElement | Cell | str
type RowType = Iterable[CellType]


class Cell:
    """
    Represents a table cell which can span multiple rows/columns, if the
    flavor supports it upon render.
    """

    __content: BaseElement
    """
    Cell content as an element.
    """

    __rspan: int
    """
    Row span.
    """

    __cspan: int
    """
    Column span.
    """

    def __init__(
        self, content: BaseElement | str, rspan: int = 1, cspan: int = 1
    ):
        self.__content = norm_obj(
            content, BaseElement, CoerceSpec(coerce_text, str)
        )
        self.__rspan = rspan
        self.__cspan = cspan

    @property
    def _element(self) -> BaseElement:
        return self.__content

    @property
    def _rspan(self) -> int:
        return self.__rspan

    @property
    def _cspan(self) -> int:
        return self.__cspan

    @property
    def _is_block(self) -> bool:
        if isinstance(self.__content, BaseInlineElement):
            return False
        elif (
            isinstance(self.__content, BlockText)
            and not self.__content._has_empty_lines
        ):
            return False
        else:
            return True

    @cache
    def _get_content(
        self, flavor: FlavorType, loose: bool, width: int | None = None
    ) -> list[str]:
        """
        Get this cell's content as a list of strings, wrapping words if
        width provided.
        """

        # render element
        lines = list(self.__content._render_element_norm(flavor))

        # if loose and no blank lines, wrap in paragraph
        if loose:
            wrap_para_cond(lines)

        if width:
            # wrap words
            wrapped_lines: list[str] = []

            for line in lines:
                wrapped_lines += self.__wrap_line(line, width)

            return wrapped_lines
        else:
            return lines

    def _get_raw_width(self, flavor: FlavorType, loose: bool) -> int:
        """
        Get width of this cell with no wrapping or explicit width from user.
        """
        return max(len(line) for line in self._get_content(flavor, loose))

    def __wrap_line(self, line: str, width: int) -> list[str]:
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
                if len(word) > width:
                    raise RenderError(
                        f"Unable to wrap line: len({word})={len(word)} > {width}"
                    )
                lines.append(line_new)
                line_new = word

        # done processing words, add last line if not empty
        if len(line_new):
            lines.append(line_new)

        return lines
