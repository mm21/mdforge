import itertools
import math
from functools import cached_property
from typing import Generator

from ......types import AlignType
from ..._context import BaseRenderContext
from ..._vcell import VirtualCell
from ...cell import Cell
from .variant import FrameTableVariant, SectionConfig, SeparatorConfig


class FrameRenderContext(BaseRenderContext[FrameTableVariant]):
    """
    Render context for frame-based tables.
    """

    def render(self) -> Generator[str, None, None]:
        assert len(self.content_vrows)

        if self.header_vrows:
            yield from self.__render_vrows(
                self.variant.header_section,
                self.header_vrows,
                next_vrow=self.content_vrows[0],
                include_upper_sep=True,
                include_lower_sep=True,
                align_lower_sep=True,
            )

        # get last row from header and first row from footer in case any
        # corners need to be overridden due to column spanning
        prev_vrow = self.header_vrows[-1] if self.header_vrows else None
        next_vrow = self.footer_vrows[0] if self.footer_vrows else None

        yield from self.__render_vrows(
            self.variant.content_section,
            self.content_vrows,
            prev_vrow=prev_vrow,
            next_vrow=next_vrow,
            include_upper_sep=self.header_vrows is None,
            include_lower_sep=self.footer_vrows is None,
            align_upper_sep=self.header_vrows is None,
        )

        if self.footer_vrows:
            assert self.variant.footer_section is not None
            yield from self.__render_vrows(
                self.variant.footer_section,
                self.footer_vrows,
                prev_vrow=self.content_vrows[-1],
                include_upper_sep=True,
                include_lower_sep=True,
            )

    @cached_property
    def content_vrows(self) -> list[list[VirtualCell]]:
        """
        Get content rows as virtual cells.
        """
        return self.__get_vrows(self.params.norm_content_rows)

    @cached_property
    def header_vrows(self) -> list[list[VirtualCell]] | None:
        """
        Get header rows as virtual cells.
        """
        if self.params.norm_header_rows is None:
            return None
        return self.__get_vrows(self.params.norm_header_rows)

    @cached_property
    def footer_vrows(self) -> list[list[VirtualCell]]:
        """
        Get footer rows as virtual cells.
        """
        if self.params.norm_footer_rows is None:
            return None
        return self.__get_vrows(self.params.norm_footer_rows)

    @cached_property
    def col_widths(self) -> list[int]:
        """
        Get column widths based on params and variant, scaling as necessary.
        Variant applies to calculation of merged cell widths based on the
        configured cell separator.
        """

        widths_pct = self.params.widths_pct
        unscaled_widths = self.__get_unscaled_widths()

        if widths_pct is None:
            return unscaled_widths

        assert len(widths_pct) == len(unscaled_widths)

        # get width percents for unscaled widths
        total_width = sum(unscaled_widths)
        unscaled_widths_pct = [
            100 * (width / total_width) for width in unscaled_widths
        ]

        # get raw factors needed to achieve target percents
        raw_scale_factors = [
            width_pct / unscaled_width_pct
            for width_pct, unscaled_width_pct in zip(
                widths_pct, unscaled_widths_pct
            )
        ]

        # scale raw factors such that the smallest one is 1.0, keeping the
        # limiting width the same
        min_raw_scale_factor = min(raw_scale_factors)
        scale_factors = [
            factor / min_raw_scale_factor for factor in raw_scale_factors
        ]

        # scale widths according to scale factors
        scaled_widths = [
            round(width * factor)
            for width, factor in zip(unscaled_widths, scale_factors)
        ]

        return scaled_widths

    def __render_vrows(
        self,
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
                prev_vrow=prev_vrow, next_vrow=vrows[0]
            )
            yield self.__render_sep_line(
                section.upper_sep_norm,
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
                    prev_vrow=vrow,
                    next_vrow=vrows[row_idx + 1] if is_middle else None,
                )

                yield self.__render_sep_line(
                    section.middle_sep,
                    seg_overrides=seg_overrides,
                    corner_overrides=corner_overrides,
                )

        # render lower separator if applicable
        if include_lower_sep:
            corner_overrides = self.__get_corner_overrides(
                prev_vrow=vrows[-1], next_vrow=next_vrow
            )
            yield self.__render_sep_line(
                section.lower_sep_norm,
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
            yield self.__render_vrow_line(vrow, row_lines, line_idx)

    def __render_vrow_line(
        self, vrow: list[VirtualCell], row_lines: list[list[str]], line_idx: int
    ):
        """
        Render a single line of a row.
        """

        # start with leading separator
        line = self.variant.row_leading_sep

        # traverse each cell and get the next segment
        for vcell, cell_lines in zip(vrow, row_lines):

            # get base segment
            seg = cell_lines[line_idx] if line_idx < len(cell_lines) else ""

            # get width, including padding if aligning using spaces
            pad_offset = 2 if self.variant.align_space else 0
            width = vcell.effective_width + pad_offset

            # pad segment to effective width using appropriate alignment
            align_char = self.__get_align_char(vcell)
            padded_seg = f"{seg:{align_char}{width}}"

            # determine which separator to use after this cell
            if vcell.is_last_col:
                # last cell in row
                sep = self.variant.row_trailing_sep
            elif vcell.cell._cspan == 1 or vcell.is_last_col_span:
                # non-spanned cell or last cell in spanned cells
                sep = self.variant.cell_sep
            else:
                # spanned cell which isn't last, don't add separator
                sep = ""

            line += padded_seg + sep

        return line

    def __render_sep_line(
        self,
        sep: SeparatorConfig,
        do_align: bool = False,
        seg_overrides: list[str | None] | None = None,
        corner_overrides: list[bool] | None = None,
    ) -> str:
        """
        Render row separator line based on configuration and table params.
        If `do_align`, use alignment chars as applicable.

        - `seg_overrides`: Used to override line segments with content for
          cells spanning multiple rows ("dangling lines")
        - `corner_overrides`: Used to override corners with normal line for
          cells spanning multiple columns
        """
        if not sep.line:
            return ""

        align_char = self.variant.align_char

        seg_overrides_ = seg_overrides or [None] * self.params.col_count
        corner_overrides_ = corner_overrides or [False] * self.params.col_count

        assert len(self.col_widths) == self.params.col_count
        assert len(self.params.col_aligns) == self.params.col_count
        assert len(seg_overrides_) == self.params.col_count
        assert len(corner_overrides_) == self.params.col_count

        # get first and last segments
        first_seg, last_seg = seg_overrides_[0], seg_overrides_[-1]

        # set corners
        left_corner = (
            sep.outer_corner_norm
            if first_seg is None
            else self.variant.row_leading_sep
        )
        right_corner = (
            sep.outer_corner_norm
            if last_seg is None
            else self.variant.row_trailing_sep
        )

        # start with left corner
        line = left_corner

        # traverse each column and get segments
        for width, col_idx, align, corner_override in zip(
            self.col_widths,
            range(self.params.col_count),
            self.params.col_aligns,
            corner_overrides_,
        ):
            is_last_col = col_idx == self.params.col_count - 1
            inner_corner = (
                sep.line if corner_override else sep.inner_corner_norm
            )

            if align_char and do_align:
                # align based on alignment chars on either side of line
                # - can only be a solid line
                assert seg_overrides_[col_idx] is None
                line += self.__get_aligned_seg(
                    sep, width, is_last_col, inner_corner, align, align_char
                )
            else:
                # solid or dangling line
                line += self.__get_sep_seg(
                    sep,
                    width,
                    is_last_col,
                    inner_corner,
                    col_idx,
                    seg_overrides_,
                )

        # end with right corner
        line += right_corner

        return line

    def __get_align_char(self, cell: VirtualCell):
        """
        Get character to use to align this cell.
        """
        match cell.align if self.variant.align_space else "left":
            case "center":
                return "^"
            case "right":
                return ">"
            case _:
                return "<"

    def __get_aligned_seg(
        self,
        sep: SeparatorConfig,
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
        line = sep.line
        assert line is not None

        left_char = align_char if align in ["left", "center"] else line
        right_char = align_char if align in ["right", "center"] else line

        seg = f"{left_char}{line * width}{right_char}"

        if not is_last_col:
            seg += inner_corner

        return seg

    def __get_sep_seg(
        self,
        sep: SeparatorConfig,
        width: int,
        is_last_col: bool,
        inner_corner: str,
        col_idx: int,
        seg_overrides: list[str | None],
    ):
        """
        Get separator line segment, either a solid line or dangling content
        from a cell spanning multiple rows.
        """

        line = sep.line
        assert line is not None

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
            line * width if seg_override is None else seg_override.ljust(width)
        )

        # append next corner if necessary
        if not is_last_col and not span_next:
            seg += inner_corner

            if next_seg_override is not None:
                # next segment will be overridden with dangling content, so
                # add space after corner
                seg += " "

        return seg

    def __get_corner_overrides(
        self,
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
                else [True] * self.params.col_count
            )

        prev_corner_overrides = get_overrides(prev_vrow)
        next_corner_overrides = get_overrides(next_vrow)

        return [
            prev and next
            for prev, next in zip(prev_corner_overrides, next_corner_overrides)
        ]

    def __get_unscaled_widths(self) -> list[int]:
        """
        Get widths accounting for widths from user or raw width of columns
        with no other constraints.
        """

        if self.params.widths is not None:
            return self.params.widths

        widths: list[int] = []

        # mapping of origin cells to their column index
        origin_map: dict[Cell, int] = {}

        for col_idx in range(self.params.col_count):

            # get max width of this column

            # list of cells and whether cell is the last spanned column
            col_cells: list[tuple[Cell, bool]] = []

            # select the cell at this column from each row
            for row in self.params.norm_effective_rows:

                cell = row[col_idx]

                # determine if this is the last spanned column: needed to
                # calculate width of spanned columns
                if cell not in origin_map:
                    # have an origin cell, add it to the map
                    origin_map[cell] = col_idx
                    is_last_col_span = False
                else:
                    # have a spanned cell, get the column index of the
                    # origin and see if this is the last spanned column
                    origin_col_idx = origin_map[cell]
                    col_idx_offset = col_idx - origin_col_idx
                    is_last_col_span = col_idx_offset == cell._cspan - 1

                col_cells.append((row[col_idx], is_last_col_span))

            assert len(col_cells) == len(self.params.effective_rows)
            widths.append(
                max(
                    self.__get_raw_width(cell, is_last_col_span)
                    for cell, is_last_col_span in col_cells
                )
            )

        return widths

    def __get_raw_width(self, cell: Cell, is_last_col_span: bool):
        """
        Get width of this cell with no other constraints.
        """

        # get raw width of original cell
        cell_width = cell._get_raw_width(self.flavor, self.params.loose)

        # if no spanned columns, just return raw cell width
        if cell._cspan == 1:
            return cell_width

        # for spanned columns, subtract the separator widths since there
        # won't be any separators between cells
        cell_width = max(
            1, cell_width - len(self.variant.cell_sep) * (cell._cspan - 1)
        )

        # divide width amongst all the columns spanned
        div_width = math.ceil(cell_width / cell._cspan)

        if is_last_col_span:
            # the last spanned column, so it may be unnecessarily long - just
            # use the remaining width
            current_width = div_width * (cell._cspan - 1)
            return max(1, cell_width - current_width)
        else:
            # not the last spanned column, this should be its width
            return div_width

    def __get_vrows(self, rows: list[list[Cell]]) -> list[list[VirtualCell]]:
        """
        Get virtual cells from cells.
        """

        row_count, col_count = len(rows), self.params.col_count

        # pre-allocate virtual rows with required dimensions
        vrows: list[list[VirtualCell]] = [
            [
                VirtualCell(self, row_idx, col_idx)
                for col_idx in range(col_count)
            ]
            for row_idx in range(row_count)
        ]

        for row_idx, col_idx in itertools.product(
            range(row_count), range(col_count)
        ):
            cell = rows[row_idx][col_idx]

            if vrows[row_idx][col_idx].cell_is_set:
                assert vrows[row_idx][col_idx].cell is cell
                continue

            # traverse this cell along with all spanned ones
            for row_offset, col_offset in itertools.product(
                range(cell._rspan), range(cell._cspan)
            ):

                # get virtual cell at this location, which should not have
                # a cell yet
                vcell = vrows[row_idx + row_offset][col_idx + col_offset]
                assert not vcell.cell_is_set

                # get origin virtual cell
                origin_vcell = vrows[row_idx][col_idx]

                # set this cell
                vcell.set_cell(cell, col_offset, origin_vcell)

        # validate: ensure each virtual cell got set
        for row_idx, col_idx in itertools.product(
            range(row_count), range(col_count)
        ):
            assert vrows[row_idx][col_idx].cell_is_set

        # set content lines
        for vrow in vrows:
            for vcell in vrow:

                if not vcell.is_spanned:
                    # no spanned cells, just set content
                    vcell.set_lines(
                        vcell.cell._get_content(
                            self.flavor,
                            self.params.loose,
                            width=vcell.effective_width,
                        )
                    )
                    continue

                elif not vcell.is_origin:
                    # spanned cells, but this is not origin cell
                    continue

                # allocate content for cell and all spanned cells
                width = self.__get_spanned_width(vrow, vcell)
                self.__allocate_content(vrows, vcell, width)

        # validate: ensure contents got set
        for row_idx, col_idx in itertools.product(
            range(row_count), range(col_count)
        ):
            assert vrows[row_idx][
                col_idx
            ].content_is_set, f"Not set at {row_idx}, {col_idx}"

        return vrows

    def __get_spanned_width(self, row: list[VirtualCell], vcell: VirtualCell):
        # add up raw widths from all spanned columns
        width: int = 0
        for col_offset in range(vcell.cell._cspan):
            width += row[vcell.col_idx + col_offset].effective_width
        return width

    def __get_vrow_height(self, vrow: list[VirtualCell]) -> int | None:
        """
        Get max height (number of lines) of this row, based only on cells which
        don't span multiple rows. Returns `None` if there are no such cells
        constraining the height.
        """

        # collect cells which don't span rows
        non_rspan_vcells = [vcell for vcell in vrow if vcell.cell._rspan == 1]

        if not len(non_rspan_vcells):
            # all cells have spanned rows
            return None

        # list of row heights
        heights: list[int] = []

        for vcell in non_rspan_vcells:

            if not vcell.is_origin:
                # skip if not origin cell, we would have already counted it
                continue

            # content for spanned cells has not yet been set
            assert not vcell.content_is_set

            # get total width of this cell and add height of resulting content
            width = self.__get_spanned_width(vrow, vcell)
            heights.append(
                len(
                    vcell.cell._get_content(
                        self.flavor, self.params.loose, width=width
                    )
                )
            )

        return max(heights) if len(heights) else None

    def __allocate_content(
        self,
        vrows: list[list[VirtualCell]],
        vcell: VirtualCell,
        width: int,
    ):
        """
        Allocate the content for this cell across all the rows/columns it
        spans, wrapping content at the given width.
        """
        assert vcell.row_idx + vcell.cell._rspan <= len(vrows)

        # get content, possibly wrapping at width of all spanned cells
        # - content is cached, so need to make copy
        content = vcell.cell._get_content(
            self.flavor, self.params.loose, width=width
        ).copy()

        # traverse each virtual row
        for row_offset in range(vcell.cell._rspan):

            # select this row
            vrow = vrows[vcell.row_idx + row_offset]

            # allocate content for this row
            self.__allocate_row_content(vrow, vcell, row_offset, content)

    def __allocate_row_content(
        self,
        vrow: list[VirtualCell],
        vcell: VirtualCell,
        row_offset: int,
        content: list[str],
    ):
        """
        Allocate content from the vcell amongst its spanned cells for this row.
        """

        # select subset of row which is spanned
        vcells = vrow[vcell.col_idx : vcell.col_idx + vcell.cell._cspan]

        # get list of widths for each spanned cell
        vcell_widths = [vcell.effective_width for vcell in vcells]

        # create list of lines per cell in this spanned row
        vcell_lines: list[list[str]] = [[] for _ in range(vcell.cell._cspan)]

        # get max height of this row
        max_height = self.__get_vrow_height(vrow)

        # loop over lines until expected height, if there is one
        line_idx = 0
        last_row = row_offset == vcell.cell._rspan - 1

        while (line_idx < (max_height or 1)) or (len(content) and last_row):
            line_idx += 1

            # consume next line of content
            line = content.pop(0) if len(content) else ""

            # divide this line among each cell in row
            segs = _split_line(line, vcell_widths)

            # append segments to each list of lines
            assert len(vcell_lines) == len(segs)
            for lines, seg in zip(vcell_lines, segs):
                lines.append(seg)

            if len(content) == 0:
                # consumed all content
                break

        # set content for each cell in row
        assert len(vcells) == len(vcell_lines)
        for vcell_iter, lines in zip(vcells, vcell_lines):
            vcell_iter.set_lines(lines)

        # if this is isn't the last row, set dangling line
        if not last_row:

            segs: list[str]

            if len(content):
                # still content, so consume the next line
                segs = _split_line(content.pop(0), vcell_widths)
            else:
                # reached end of content, use empty strings for segments
                segs = [""] * len(vcell_widths)

            # set dangling lines
            assert len(vcells) == len(segs)
            for vcell_iter, seg in zip(vcells, segs):
                vcell_iter.set_dangling_line(seg)


def _split_line(line: str, widths: list[int]) -> list[str]:
    """
    Split line into segments of provided widths. If line is consumed before
    all segments have been added with respective widths, the remaining widths
    are truncated or set to empty strings.
    """
    assert len(line) <= sum(widths)

    segs: list[str] = []

    start_offset = 0
    for width in widths:
        assert start_offset <= len(line)

        seg: str

        # get segment of this content line
        if start_offset < len(line):
            # consume the next part of line, starting with
            # start_offset

            end_offset = min(start_offset + width, len(line))
            seg = line[start_offset:end_offset]

            # advance start offset
            start_offset += len(seg)
        else:
            # reached end of line, just use empty string
            seg = ""

        segs.append(seg)

    return segs
