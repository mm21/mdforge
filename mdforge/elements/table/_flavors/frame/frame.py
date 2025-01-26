from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from ..._context import RenderContext
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
        context: RenderContext,
        align_char: str | None = None,
        do_align: bool = False,
    ) -> str:
        """
        Get line based on configuration and table params. If `do_align`, use
        alignment chars as applicable.
        """
        if not self.line:
            return ""

        segs: list[str] = []

        for width, align in zip(context.col_widths, context.col_aligns):

            # adjust to include spacing between cells
            line_width = width + 2

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
    upper_sep: SeparatorConfig | None = None  # defaults to sep
    lower_sep: SeparatorConfig | None = None  # defaults to sep

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

    def render(self, context: RenderContext) -> Generator[str, None, None]:
        """
        Render this table using the provided params.
        """

        if context.params.header:
            yield from self.__render_rows(
                context,
                context.params.header,
                self.header_section,
                include_upper_sep=True,
                include_lower_sep=True,
                align_lower_sep=True,
            )

        yield from self.__render_rows(
            context,
            context.params.rows,
            self.content_section,
            include_upper_sep=context.params.header is None,
            include_lower_sep=context.params.footer is None,
            align_upper_sep=context.params.header is None,
        )

        if context.params.footer:
            assert self.footer_section is not None
            yield from self.__render_rows(
                context,
                context.params.footer,
                self.footer_section,
                include_upper_sep=True,
                include_lower_sep=True,
            )

    def __render_rows(
        self,
        context: RenderContext,
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

        # render upper separator if applicable
        if include_upper_sep:
            yield section._upper_sep.get_line(
                context, align_char=self.align_char, do_align=align_upper_sep
            )

        # render rows
        sep_line = section.middle_sep.get_line(context)
        for row_idx, row in enumerate(rows):

            # render this row
            yield from self.__render_row(context, row)

            # render middle separator, if not last row or have a single row
            # with rows separated by spaces
            is_middle = row_idx != len(rows) - 1
            has_trailing_line = (
                section.middle_sep.line is None and len(rows) == 1
            )

            if is_middle or has_trailing_line:
                yield sep_line

        # render lower separator if applicable
        if include_lower_sep:
            yield section._lower_sep.get_line(
                context, align_char=self.align_char, do_align=align_lower_sep
            )

    def __render_row(
        self,
        context: RenderContext,
        row: list[Cell],
    ) -> Generator[str, None, None]:
        """
        Render a single row without any separator.
        """

        assert len(row) == len(context.col_widths)

        # get list of lines per column
        row_lines = [
            cell._get_content(
                context.flavor,
                width=col_width if context.variant.wrap else None,
            )
            for cell, col_width in zip(row, context.col_widths)
        ]

        # get max lines per column
        max_lines = max(len(lines) for lines in row_lines)

        for line_idx in range(max_lines):

            # segments for this row line
            segs: list[str] = []

            for cell_lines, col_width, col_align in zip(
                row_lines, context.col_widths, context.col_aligns
            ):

                pad_space = "" if self.cell_sep is None else " "
                width_offset = 2 if self.cell_sep is None else 0

                content = (
                    cell_lines[line_idx] if line_idx < len(cell_lines) else ""
                )

                # validate width of this line
                assert (
                    len(content) <= col_width
                ), f"Cell line of width {len(content)} does not fit in column of width {col_width}"

                # align using spaces if applicable
                if self.align_space:
                    match col_align:
                        case "center":
                            align_char = "^"
                        case "right":
                            align_char = ">"
                        case _:
                            align_char = "<"
                else:
                    align_char = "<"

                width = col_width + width_offset
                line = f"{content:{align_char}{width}}"
                segs.append(f"{pad_space}{line}{pad_space}")

            outer_sep = self.cell_sep or ""
            inner_sep = self.cell_sep or " "
            yield f"{outer_sep}{inner_sep.join(segs)}{outer_sep}"
