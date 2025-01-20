from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Generator

from .....types import FlavorType
from ..._params import TableParams
from ...cell import Cell
from ..flavor import BaseTableVariant

__all__ = [
    "SeparatorConfig",
    "SectionConfig",
    "FrameTableVariant",
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
        variant: FrameTableVariant,
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

        segs: list[str] = []

        for col_idx in range(params.col_count):

            width = widths[col_idx]
            align = params.col_aligns[col_idx]

            # adjust to include spacing between cells
            line_width = width + 2

            if variant.align_char and do_align:
                # align based on alignment chars on either side of line
                inner_width = width
                left_char = (
                    variant.align_char
                    if align in ["left", "center"]
                    else self.line
                )
                right_char = (
                    variant.align_char
                    if align in ["right", "center"]
                    else self.line
                )
            else:
                # solid line
                inner_width = line_width
                left_char, right_char = "", ""

            inner_line = self.line * inner_width
            segs.append(f"{left_char}{inner_line}{right_char}")

        return self._inner_corner.join(segs).join(
            [self._outer_corner, self._outer_corner]
        )

    @property
    def _inner_corner(self) -> str | None:
        return (
            self.inner_corner
            if self.inner_corner is not None
            else (self.corner if self.corner is not None else self.line)
        )
        # return self.inner_corner or self.corner

    @property
    def _outer_corner(self) -> str | None:
        return (
            self.outer_corner
            if self.outer_corner is not None
            else (self.corner if self.corner is not None else self.line)
        )
        # return self.outer_corner or self.corner


@dataclass(frozen=True)
class SectionConfig:
    """
    Encapsulates section info, i.e. header/content/footer.
    """

    middle_sep: SeparatorConfig
    upper_sep: SeparatorConfig | None = None  # defaults to sep
    lower_sep: SeparatorConfig | None = None  # defaults to sep


@dataclass(frozen=True)
class FrameTableVariant(BaseTableVariant):
    """
    Encapsulates frame table construction info.
    """

    header_section: SectionConfig
    content_section: SectionConfig
    footer_section: SectionConfig | None = None

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

    def render(
        self, flavor: FlavorType, params: TableParams
    ) -> Generator[str, None, None]:
        """
        Render this table using the provided params.
        """

        if params.header:
            yield from self.__render_rows(
                flavor,
                params,
                params.header,
                self.header_section,
                include_upper_sep=True,
                include_lower_sep=True,
                align_lower_sep=True,
            )

        yield from self.__render_rows(
            flavor,
            params,
            params.rows,
            self.content_section,
            include_upper_sep=params.header is None,
            include_lower_sep=params.footer is None,
            align_upper_sep=params.header is None,
        )

        if params.footer:
            assert self.footer_section is not None
            yield from self.__render_rows(
                flavor,
                params,
                params.footer,
                self.footer_section,
                include_upper_sep=True,
                include_lower_sep=True,
            )

    def __render_rows(
        self,
        flavor: FlavorType,
        params: TableParams,
        rows: list[list[Cell]],
        section: SectionConfig,
        include_upper_sep: bool = False,
        include_lower_sep: bool = False,
        align_upper_sep: bool = False,
        align_lower_sep: bool = False,
    ) -> Generator[str, None, None]:
        """
        Yield lines for rows, separated by separator (between rows) and
        optional upper/lower separators.
        """

        widths = self.__get_col_widths(flavor, params)

        # generate upper separator if applicable
        if include_upper_sep:
            sep = section.upper_sep or section.middle_sep
            yield sep.get_line(self, params, widths, do_align=align_upper_sep)

        # generate rows
        sep_line = section.middle_sep.get_line(self, params, widths)
        for row_idx, row in enumerate(rows):
            yield from self.__render_row(
                flavor, params, rows, section, row_idx, row, sep_line
            )

        # generate lower separator if applicable
        if include_lower_sep:
            sep = section.lower_sep or section.middle_sep
            yield sep.get_line(self, params, widths, do_align=align_lower_sep)

    def __render_row(
        self,
        flavor: FlavorType,
        params: TableParams,
        rows: list[list[Cell]],
        section: SectionConfig,
        row_idx: int,
        row: list[Cell],
        sep_line: str,
    ) -> Generator[str, None, None]:
        """
        Render a single row.
        """
        widths = self.__get_col_widths(flavor, params)
        row_lines = [cell._get_content(flavor) for cell in row]
        max_lines = max(len(lines) for lines in row_lines)

        assert len(widths) == params.col_count
        assert len(row_lines) == params.col_count

        for line_idx in range(max_lines):

            # segments for this row line
            segs: list[str] = []

            for col_idx, cell_lines in enumerate(row_lines):

                pad_space = "" if self.cell_sep is None else " "
                width_offset = 2 if self.cell_sep is None else 0

                content = (
                    cell_lines[line_idx] if line_idx < len(cell_lines) else ""
                )

                # align using spaces if applicable
                if self.align_space:
                    match params.col_aligns[col_idx]:
                        case "center":
                            align_char = "^"
                        case "right":
                            align_char = ">"
                        case _:
                            align_char = "<"
                else:
                    align_char = "<"

                width = widths[col_idx] + width_offset
                line = f"{content:{align_char}{width}}"
                segs.append(f"{pad_space}{line}{pad_space}")

            outer_sep = self.cell_sep or ""
            inner_sep = self.cell_sep or " "
            yield f"{outer_sep}{inner_sep.join(segs)}{outer_sep}"

        # include a row separator, if not last row or have a single-row
        # table with rows separated by spaces (line chars)
        is_middle = row_idx != len(rows) - 1
        has_trailing_line = section.middle_sep.line is None and len(rows) == 1
        if is_middle or has_trailing_line:
            yield sep_line

    @cache
    def __get_col_widths(
        self, flavor: FlavorType, params: TableParams
    ) -> list[int]:
        """
        Get final widths of the content in each column.
        """
        calc_widths = self.__calc_widths(flavor, params)
        if params.widths:
            # ensure content fits in provided widths
            assert len(params.widths) == len(calc_widths)
            for width, calc_width in zip(params.widths, calc_widths):
                assert (
                    width >= calc_width
                ), f"Provided width {width} less than content width {calc_width}"
            return params.widths
        else:
            return calc_widths

    @cache
    def __calc_widths(self, flavor: FlavorType, params: TableParams):
        """
        Calculate column widths based on row contents.
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
