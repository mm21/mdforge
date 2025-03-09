from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from ......exceptions import RenderError
from ......types import AlignType
from ..._context import RenderContext
from ..._params import TableParams
from ..._vcell import VirtualCell
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
        seg_overrides: list[str | None] | None = None,
        corner_overrides: list[bool] | None = None,
    ) -> str:
        """
        Get line based on configuration and table params. If `do_align`, use
        alignment chars as applicable.

        - `seg_overrides`: Used to override line segments with content for
          cells spanning multiple rows ("dangling lines")
        - `corner_overrides`: Used to override corners with normal line for
          cells spanning multiple columns
        """
        if not self.line:
            return ""

        align_char = context.variant.align_char

        seg_overrides_ = seg_overrides or [None] * context.params.col_count
        corner_overrides_ = (
            corner_overrides or [False] * context.params.col_count
        )

        assert len(context.col_widths) == context.params.col_count
        assert len(context.params.col_aligns) == context.params.col_count
        assert len(seg_overrides_) == context.params.col_count
        assert len(corner_overrides_) == context.params.col_count

        # get first and last segments
        first_seg, last_seg = seg_overrides_[0], seg_overrides_[-1]

        # set corners
        left_corner = (
            self.__outer_corner
            if first_seg is None
            else context.variant.row_leading_sep
        )
        right_corner = (
            self.__outer_corner
            if last_seg is None
            else context.variant.row_trailing_sep
        )

        # start with left corner
        line = left_corner

        # traverse each column and get segments
        for width, col_idx, align, corner_override in zip(
            context.col_widths,
            range(context.params.col_count),
            context.params.col_aligns,
            corner_overrides_,
        ):
            is_last_col = col_idx == context.params.col_count - 1
            inner_corner = self.line if corner_override else self.__inner_corner

            if align_char and do_align:
                # align based on alignment chars on either side of line
                # - can only be a solid line
                assert seg_overrides_[col_idx] is None
                line += self.__get_aligned_seg(
                    width, is_last_col, inner_corner, align, align_char
                )
            else:
                # solid or dangling line
                line += self.__get_seg(
                    width, is_last_col, inner_corner, col_idx, seg_overrides_
                )

        # end with right corner
        line += right_corner

        return line

    @property
    def __inner_corner(self) -> str:
        return (
            self.inner_corner
            if self.inner_corner is not None
            else self.__default_corner
        )

    @property
    def __outer_corner(self) -> str:
        return (
            self.outer_corner
            if self.outer_corner is not None
            else self.__default_corner
        )

    @property
    def __default_corner(self) -> str:
        return (self.corner if self.corner is not None else self.line) or ""

    def __get_aligned_seg(
        self,
        width: int,
        is_last_col: bool,
        inner_corner: str,
        align: AlignType,
        align_char: str,
    ) -> str:
        """
        Get line segment with alignment set by characters adjacent to corners.
        Can only be used for line between header and content or (if no header)
        the first line before content. Therefore this line cannot have any
        dangling content segments.
        """

        left_char = align_char if align in ["left", "center"] else self.line
        right_char = align_char if align in ["right", "center"] else self.line

        seg = f"{left_char}{self.line * width}{right_char}"

        if not is_last_col:
            seg += inner_corner

        return seg

    def __get_seg(
        self,
        width: int,
        is_last_col: bool,
        inner_corner: str,
        col_idx: int,
        seg_overrides: list[str | None],
    ):
        """
        Get line segment, either a solid line or dangling content from a cell
        spanning multiple rows.
        """

        seg_override = seg_overrides[col_idx]

        # get next override segment, if any
        next_seg_override = (
            seg_overrides[col_idx + 1] if not is_last_col else None
        )

        # check if this segment spans to the next one
        span_next = all(
            seg is not None for seg in [seg_override, next_seg_override]
        )

        # adjust width if necessary to reach next corner
        if seg_override is None or not is_last_col:
            width += 2 if span_next or seg_override is None else 1

        # create segment of required width using line char or override
        seg = (
            self.line * width
            if seg_override is None
            else seg_override.ljust(width)
        )

        # append next corner if necessary
        if not is_last_col and not span_next:
            seg += inner_corner

            if next_seg_override is not None:
                # next segment will be overridden with dangling content, so
                # add space after corner
                seg += " "

        return seg


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

    name: str
    header_section: SectionConfig
    content_section: SectionConfig
    footer_section: SectionConfig | None = None

    # TODO: most of this logic belongs in RenderContext, keeping
    # this class as a simple dataclass

    def validate_params(self, params: TableParams):

        if params.footer_rows and not self.footer_section:
            raise RenderError(
                f"Table variant '{self.name}' does not support footer rows, try passing block=True"
            )

    def render(self, context: RenderContext) -> Generator[str, None, None]:
        """
        Render this table using the provided params.
        """

        assert len(context.content_vrows)

        if context.header_vrows:
            yield from self.__render_vrows(
                context,
                self.header_section,
                context.header_vrows,
                next_vrow=context.content_vrows[0],
                include_upper_sep=True,
                include_lower_sep=True,
                align_lower_sep=True,
            )

        # get last row from header and first row from footer in case any
        # corners need to be overridden due to column spanning
        prev_vrow = context.header_vrows[-1] if context.header_vrows else None
        next_vrow = context.footer_vrows[0] if context.footer_vrows else None

        yield from self.__render_vrows(
            context,
            self.content_section,
            context.content_vrows,
            prev_vrow=prev_vrow,
            next_vrow=next_vrow,
            include_upper_sep=context.header_vrows is None,
            include_lower_sep=context.footer_vrows is None,
            align_upper_sep=context.header_vrows is None,
        )

        if context.footer_vrows:
            assert self.footer_section is not None
            yield from self.__render_vrows(
                context,
                self.footer_section,
                context.footer_vrows,
                prev_vrow=context.content_vrows[-1],
                include_upper_sep=True,
                include_lower_sep=True,
            )

    def __render_vrows(
        self,
        context: RenderContext,
        section: SectionConfig,
        vrows: list[list[VirtualCell]],
        prev_vrow: list[VirtualCell] | None = None,
        next_vrow: list[VirtualCell] | None = None,
        include_upper_sep: bool = False,
        include_lower_sep: bool = False,
        align_upper_sep: bool = False,
        align_lower_sep: bool = False,
    ) -> Generator[str, None, None]:
        """
        Yield lines for rows, separated by separator (between rows) and
        optional upper/lower separators.
        """

        row_count = len(vrows)
        assert row_count > 0

        # render upper separator if applicable
        if include_upper_sep:
            corner_overrides = self.__get_corner_overrides(
                context, prev_vrow=prev_vrow, next_vrow=vrows[0]
            )
            yield section._upper_sep.get_line(
                context,
                do_align=align_upper_sep,
                corner_overrides=corner_overrides,
            )

        # render rows
        for row_idx, vrow in enumerate(vrows):

            # render this row
            yield from self.__render_vrow(vrow)

            # render middle separator, if not last row or have a single row
            # with rows separated by spaces
            is_middle = row_idx != row_count - 1
            has_trailing_line = (
                section.middle_sep.line is None and row_count == 1
            )

            if is_middle or has_trailing_line:

                # get segment overrides from dangling lines
                seg_overrides = [cell.dangling_line for cell in vrow]

                # get corner overrides from row spans for this/next rows
                corner_overrides = self.__get_corner_overrides(
                    context,
                    prev_vrow=vrow,
                    next_vrow=vrows[row_idx + 1] if is_middle else None,
                )

                yield section.middle_sep.get_line(
                    context,
                    seg_overrides=seg_overrides,
                    corner_overrides=corner_overrides,
                )

        # render lower separator if applicable
        if include_lower_sep:
            corner_overrides = self.__get_corner_overrides(
                context, prev_vrow=vrows[-1], next_vrow=next_vrow
            )
            yield section._lower_sep.get_line(
                context,
                do_align=align_lower_sep,
                corner_overrides=corner_overrides,
            )

    def __render_vrow(
        self, vrow: list[VirtualCell]
    ) -> Generator[str, None, None]:
        """
        Render a single row without any inter-row separator.
        """

        # get list of lines per column
        row_lines = [vcell.lines for vcell in vrow]

        # get max lines per column
        max_lines = max(len(lines) for lines in row_lines)

        # render each line
        for line_idx in range(max_lines):
            yield self.__render_line(vrow, row_lines, line_idx)

    def __render_line(
        self, vrow: list[VirtualCell], row_lines: list[list[str]], line_idx: int
    ):
        """
        Render a single line of a row.
        """

        # start with leading separator
        line = self.row_leading_sep

        # traverse each cell and get the next segment
        for vcell, cell_lines in zip(vrow, row_lines):

            # get base segment
            seg = cell_lines[line_idx] if line_idx < len(cell_lines) else ""

            # get width, including padding if aligning using spaces
            pad_offset = 2 if self.align_space else 0
            width = vcell.effective_width + pad_offset

            # pad segment to effective width using appropriate alignment
            align_char = self.__get_align_char(vcell)
            padded_seg = f"{seg:{align_char}{width}}"

            # determine which separator to use after this cell
            if vcell.is_last_col:
                # last cell in row
                sep = self.row_trailing_sep
            elif vcell.cell._cspan == 1 or vcell.is_last_col_span:
                # non-spanned cell or last cell in spanned cells
                sep = self.cell_sep
            else:
                # spanned cell which isn't last, don't add separator
                sep = ""

            line += padded_seg + sep

        return line

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

    def __get_corner_overrides(
        self,
        context: RenderContext,
        *,
        prev_vrow: list[VirtualCell] | None,
        next_vrow: list[VirtualCell] | None,
    ) -> list[bool]:
        """
        Get list of which inner corners to override with a normal line in
        case of the same columns being spanned before/after the line, or
        the first/last row having any spanned columns.

        For example, required to go from this:

                        (Inner corners here need to be replaced)
                                      |       |
                                      V       V
        +---------------------+-------+-------+-------+
        | Location            | Temperature 1961-1990 |
        |                     | in degree Celsius     |
        |                     +-------+-------+-------+
        |                     | min   | mean  | max   |
        +=====================+=======+=======+=======+

        To this:

        +---------------------+-----------------------+
        | Location            | Temperature 1961-1990 |
        |                     | in degree Celsius     |
        |                     +-------+-------+-------+
        |                     | min   | mean  | max   |
        +=====================+=======+=======+=======+
        """

        def get_overrides(vrow: list[VirtualCell] | None) -> list[bool]:
            return (
                [
                    vcell.cell._cspan > 1 and not vcell.is_last_col_span
                    for vcell in vrow
                ]
                if vrow
                else [True] * context.params.col_count
            )

        prev_corner_overrides = get_overrides(prev_vrow)
        next_corner_overrides = get_overrides(next_vrow)

        return [
            prev and next
            for prev, next in zip(prev_corner_overrides, next_corner_overrides)
        ]
