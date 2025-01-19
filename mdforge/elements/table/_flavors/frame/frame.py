from __future__ import annotations

from dataclasses import dataclass
from functools import cache, cached_property
from typing import Generator

from .....types import FlavorType
from ..._params import TableParams
from ...cell import Cell
from ..flavor import BaseTableConfig

__all__ = [
    "SeparatorConfig",
    "SectionConfig",
    "FrameTableConfig",
]


@dataclass(frozen=True)
class SeparatorConfig:
    """
    Encapsulates a table separator.
    """

    line: str | None = "-"
    """
    Base character for the line, i.e. "-" or "=".
    """

    inner_corner: str | None = None
    """
    Innermost corner character.
    """

    outer_corner: str | None = None
    """
    Outermost corner character.
    """

    corner: str | None = None
    """
    Corner character for both inner and outer corners.
    """

    def get_line(
        self,
        config: FrameTableConfig,
        params: TableParams,
        widths: list[int],
        do_align: bool = False,
    ) -> str:
        """
        Get line based on configuration and table params. If `do_align`, use
        alignment chars as applicable.
        """
        if not self.line:
            return ""

        inner_corner = self._inner_corner or self.line
        outer_corner = (
            (self._outer_corner or self.line) if config.cell_sep else ""
        )

        segs: list[str] = []

        for col_idx in range(params.col_count):

            width = widths[col_idx]
            align = params.col_aligns[col_idx]

            line_width = width + config.cell_spacing

            if config.align_char and do_align:
                # align based on alignment chars on either side of line
                assert line_width > 2
                inner_width = line_width - 2
                left_char = (
                    config.align_char
                    if align in ["left", "center"]
                    else self.line
                )
                right_char = (
                    config.align_char
                    if align in ["right", "center"]
                    else self.line
                )
            else:
                # solid line
                inner_width = line_width
                left_char, right_char = "", ""

            inner_line = self.line * inner_width
            segs.append(f"{left_char}{inner_line}{right_char}")

        return inner_corner.join(segs).join([outer_corner, outer_corner])

    @property
    def _inner_corner(self) -> str | None:
        return self.inner_corner or self.corner

    @property
    def _outer_corner(self) -> str | None:
        return self.outer_corner or self.corner


@dataclass(frozen=True)
class SectionConfig:
    """
    Encapsulates section info, i.e. header/content/footer.
    """

    middle_sep: SeparatorConfig
    upper_sep: SeparatorConfig | None = None  # defaults to sep
    lower_sep: SeparatorConfig | None = None  # defaults to sep


@dataclass(frozen=True)
class FrameTableConfig(BaseTableConfig):
    """
    Encapsulates frame table construction info.
    """

    header_section: SectionConfig
    content_section: SectionConfig
    footer_section: SectionConfig

    cell_sep: str | None = None
    """
    Cell separator, e.g. "|".
    """

    align_char: str | None = None
    """
    Character used to indicate alignment within a separator, e.g. ":" for
    `pandoc`.
    """

    align_space: bool = False
    """
    Whether alignment should be indicated by using spaces in the header.
    """

    @cached_property
    def cell_spacing(self) -> int:
        """
        Number of additional spaces in between each cell.
        """
        return 1 if self.cell_sep is None else 2

    def render(
        self, flavor: FlavorType, params: TableParams
    ) -> Generator[str, None, None]:
        """
        Render this table using the provided params.
        """

        if params.header:
            yield from self._render_rows(
                flavor,
                params,
                params.header,
                self.header_section,
                include_upper=True,
                include_lower=True,
                align_lower=True,
            )

        yield from self._render_rows(
            flavor,
            params,
            params.rows,
            self.content_section,
            include_upper=params.header is None,
            include_lower=params.footer is None,
            align_upper=params.header is None,
        )

        if params.footer:
            yield from self._render_rows(
                flavor,
                params,
                params.footer,
                self.footer_section,
                include_upper=True,
                include_lower=True,
            )

    def _render_rows(
        self,
        flavor: FlavorType,
        params: TableParams,
        rows: list[list[Cell]],
        section: SectionConfig,
        include_upper: bool = False,
        include_lower: bool = False,
        align_upper: bool = False,
        align_lower: bool = False,
    ) -> Generator[str, None, None]:
        """
        Yield lines for rows, separated by separator (between rows) and
        optional upper/lower separators.
        """

        widths = self.__get_col_widths(flavor, params)
        sep_line = section.middle_sep.get_line(self, params, widths)

        if include_upper:
            sep = section.upper_sep or section.middle_sep
            yield sep.get_line(self, params, widths, do_align=align_upper)

        for row_idx, row in enumerate(rows):

            row_lines = [cell._get_content(flavor) for cell in row]
            max_lines = max(len(lines) for lines in row_lines)

            for line_idx in range(max_lines):

                # segments for this row line
                segs: list[str] = []

                for cell_idx, cell_lines in enumerate(row_lines):

                    leading_space = "" if self.cell_sep is None else " "
                    trailing_space = " "

                    content = (
                        cell_lines[line_idx]
                        if line_idx < len(cell_lines)
                        else ""
                    )

                    # check if table is aligned using spaces
                    if self.align_space:

                        # is header and align by using spaces
                        assert cell_idx < len(params.col_aligns)

                        match params.col_aligns[cell_idx]:
                            case "center":
                                align_char = "^"
                            case "right":
                                align_char = ">"
                            case _:
                                align_char = "<"
                    else:
                        align_char = "<"

                    width_offset = (
                        (len(leading_space) + len({trailing_space}))
                        if self.cell_sep is None
                        else 0
                    )
                    width = widths[cell_idx] + width_offset
                    line = f"{content:{align_char}{width}}"
                    segs.append(f"{leading_space}{line}{trailing_space}")

                cell_sep = self.cell_sep or ""
                yield cell_sep + cell_sep.join(segs) + cell_sep

            # include a row separator, if not last row or have a single-row
            # table with rows separated by spaces (line chars)
            is_middle = row_idx != len(rows) - 1
            has_trailing_line = (
                section.middle_sep.line is None and len(rows) == 1
            )
            if is_middle or has_trailing_line:
                yield sep_line

        if include_lower:
            sep = section.lower_sep or section.middle_sep
            yield sep.get_line(self, params, widths, do_align=align_lower)

    @cache
    def __get_col_widths(
        self, flavor: FlavorType, params: TableParams
    ) -> list[int]:
        """
        Get widths of the content in each column.
        """

        effective_widths = self.__get_widths(flavor, params)
        raw_widths = params.widths if params.widths else effective_widths

        if not self.align_space:
            # if not aligning based on space, use raw widths
            return raw_widths

        # if aligning based on space, allow 1 extra char to ensure
        # widths are wide enough for content to be aligned via spaces
        return [
            max(raw_width, effective_width + 1)
            for raw_width, effective_width in zip(raw_widths, effective_widths)
        ]

    @cache
    def __get_widths(self, flavor: FlavorType, params: TableParams):
        """
        Get widths of the provided rows.
        """
        widths: list[int] = [0] * params.col_count
        for row in params.effective_rows:
            assert len(row) == len(widths)
            for i, cell in enumerate(row):
                widths[i] = max(
                    widths[i],
                    *(len(line) for line in cell._get_content(flavor)),
                )
        return widths
