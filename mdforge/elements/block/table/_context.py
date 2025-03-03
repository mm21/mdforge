"""
Encapsulates context for rendering tables.
"""

import itertools
import math
from dataclasses import dataclass
from functools import cached_property

from ....types import FlavorType
from ._flavors.flavor import BaseTableVariant
from ._params import TableParams
from ._vcell import VirtualCell
from .cell import Cell


@dataclass(frozen=True)
class RenderContext:

    flavor: FlavorType
    variant: BaseTableVariant
    params: TableParams

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
