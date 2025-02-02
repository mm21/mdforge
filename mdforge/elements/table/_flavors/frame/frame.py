from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from ..._context import RenderContext
from ...cell import VirtualCell
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
        context: RenderContext,
        do_align: bool = False,
    ) -> str:
        """
        Get line based on configuration and table params. If `do_align`, use
        alignment chars as applicable.
        """
        if not self.line:
            return ""

        segs: list[str] = []
        align_char = context.variant.align_char

        for width, align in zip(context.col_widths, context.params.col_aligns):

            if align_char and do_align:
                # align based on alignment chars on either side of line
                inner_width = width
                left_char = (
                    align_char if align in ["left", "center"] else self.line
                )
                right_char = (
                    align_char if align in ["right", "center"] else self.line
                )
            else:
                # solid line
                inner_width = width + 2
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

    @property
    def _outer_corner(self) -> str | None:
        return (
            self.outer_corner
            if self.outer_corner is not None
            else (self.corner if self.corner is not None else self.line)
        )


@dataclass(frozen=True)
class SectionConfig:
    """
    Encapsulates section info, i.e. header/content/footer.
    """

    middle_sep: SeparatorConfig
    upper_sep: SeparatorConfig | None = None
    lower_sep: SeparatorConfig | None = None

    @property
    def _upper_sep(self) -> SeparatorConfig:
        return self.upper_sep or self.middle_sep

    @property
    def _lower_sep(self) -> SeparatorConfig:
        return self.lower_sep or self.middle_sep


@dataclass(frozen=True)
class FrameTableVariant(BaseTableVariant):
    """
    Encapsulates frame table construction info.
    """

    header_section: SectionConfig
    content_section: SectionConfig
    footer_section: SectionConfig | None = None

    def render(self, context: RenderContext) -> Generator[str, None, None]:
        """
        Render this table using the provided params.
        """

        if context.virtual_header_rows:
            yield from self.__render_rows(
                context,
                context.virtual_header_rows,
                self.header_section,
                include_upper_sep=True,
                include_lower_sep=True,
                align_lower_sep=True,
            )

        yield from self.__render_rows(
            context,
            context.virtual_content_rows,
            self.content_section,
            include_upper_sep=context.virtual_header_rows is None,
            include_lower_sep=context.virtual_footer_rows is None,
            align_upper_sep=context.virtual_header_rows is None,
        )

        if context.virtual_footer_rows:
            assert self.footer_section is not None
            yield from self.__render_rows(
                context,
                context.virtual_footer_rows,
                self.footer_section,
                include_upper_sep=True,
                include_lower_sep=True,
            )

    def __render_rows(
        self,
        context: RenderContext,
        virtual_rows: list[list[VirtualCell]],
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

        row_count = len(virtual_rows)

        # render upper separator if applicable
        if include_upper_sep:
            yield section._upper_sep.get_line(context, do_align=align_upper_sep)

        # render rows
        sep_line = section.middle_sep.get_line(context)
        for row_idx, row in enumerate(virtual_rows):

            # render this row
            yield from self.__render_row(context, row)

            # render middle separator, if not last row or have a single row
            # with rows separated by spaces
            is_middle = row_idx != row_count - 1
            has_trailing_line = (
                section.middle_sep.line is None and len(virtual_rows) == 1
            )

            if is_middle or has_trailing_line:
                yield sep_line

        # render lower separator if applicable
        if include_lower_sep:
            yield section._lower_sep.get_line(context, do_align=align_lower_sep)

    def __render_row(
        self,
        context: RenderContext,
        row: list[VirtualCell],
    ) -> Generator[str, None, None]:
        """
        Render a single row without any separator.
        """

        assert len(row) == len(context.col_widths)

        # get list of lines per column
        row_lines = [list(cell.get_content()) for cell in row]

        # get max lines per column
        max_lines = max(len(lines) for lines in row_lines)

        for line_idx in range(max_lines):

            line = self.row_leading_sep

            # traverse each cell and get the next segment
            for cell, cell_lines in zip(row, row_lines):

                # get segment
                seg = cell_lines[line_idx] if line_idx < len(cell_lines) else ""

                pad_offset = 2 if self.align_space else 0

                if cell.cell.cspan > 1:
                    # include the cell separator if cell is being spanned
                    span_offset = (
                        0 if cell._is_last_col_span else len(self.cell_sep)
                    )
                else:
                    span_offset = 0

                # get final width
                width = cell.final_width + pad_offset + span_offset

                # pad segment using appropriate alignment
                align_char = self.__get_align_char(cell)
                padded_seg = f"{seg:{align_char}{width}}"

                # determine which separator to use after this cell
                if cell._is_last_col:
                    # last cell in row
                    sep = self.row_trailing_sep
                elif cell.cell.cspan == 1 or cell._is_last_col_span:
                    # non-spanned cell or last cell in spanned cells
                    sep = self.cell_sep
                else:
                    # spanned cell which isn't last, don't add separator
                    sep = ""

                line += padded_seg + sep

            yield line

    def __get_align_char(self, cell: VirtualCell):
        """
        Get character to use to align this cell.
        """
        match cell.align if self.align_space else "left":
            case "center":
                return "^"
            case "right":
                return ">"
            case _:
                return "<"
