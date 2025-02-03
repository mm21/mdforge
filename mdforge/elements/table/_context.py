"""
Encapsulates context for rendering tables.
"""

import itertools
import math
from dataclasses import dataclass
from functools import cached_property

from ...types import FlavorType
from ._flavors.flavor import BaseTableVariant
from ._params import TableParams
from .cell import Cell, VirtualCell


@dataclass(frozen=True)
class RenderContext:

    flavor: FlavorType
    variant: BaseTableVariant
    params: TableParams

    @cached_property
    def virtual_content_rows(self) -> list[list[VirtualCell]]:
        """
        Get content rows as virtual cells.
        """
        return self.__get_virtual_rows(self.params.norm_content_rows)

    @cached_property
    def virtual_header_rows(self) -> list[list[VirtualCell]] | None:
        """
        Get header rows as virtual cells.
        """
        if self.params.norm_header_rows is None:
            return None
        return self.__get_virtual_rows(self.params.norm_header_rows)

    @cached_property
    def virtual_footer_rows(self) -> list[list[VirtualCell]]:
        """
        Get footer rows as virtual cells.
        """
        if self.params.norm_footer_rows is None:
            return None
        return self.__get_virtual_rows(self.params.norm_footer_rows)

    @cached_property
    def col_widths(self) -> list[int]:
        """
        Get normalized widths based on params and variant.
        """

        widths: list[int] = []
        param_widths: list[int | None] = (
            self.params.widths or [None] * self.params.col_count
        )

        assert len(param_widths) == self.params.col_count

        # mapping of origin cells to their column index
        origin_map: dict[Cell, int] = {}

        for col_idx, width in enumerate(param_widths):

            if width:
                # width passed from user
                widths.append(width)
            else:
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
                        is_last_col_span = col_idx_offset == cell.cspan - 1

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
        cell_width = cell._get_raw_width(self.flavor)

        # if no spanned columns, just return raw cell width
        if cell.cspan == 1:
            return cell_width

        # for spanned columns, subtract the separator widths since there
        # won't be any separators between cells
        cell_width = max(
            1, cell_width - len(self.variant.cell_sep) * (cell.cspan - 1)
        )

        # divide width amongst all the columns spanned
        div_width = math.ceil(cell_width / cell.cspan)

        if is_last_col_span:
            # the last spanned column, so it may be unnecessarily long - just
            # use the remaining width
            current_width = div_width * (cell.cspan - 1)
            return max(1, cell_width - current_width)
        else:
            # not the last spanned column, this should be its width
            return div_width

    def __get_virtual_rows(
        self, rows: list[list[Cell]]
    ) -> list[list[VirtualCell]]:
        """
        Get virtual cells from cells.
        """

        row_count, col_count = len(rows), self.params.col_count

        # pre-allocate virtual rows with required dimensions
        virtual_rows: list[list[VirtualCell]] = [
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

            if virtual_rows[row_idx][col_idx].cell_is_set:
                assert virtual_rows[row_idx][col_idx].cell is cell
                continue

            # traverse this cell along with all spanned ones
            for row_offset, col_offset in itertools.product(
                range(cell.rspan), range(cell.cspan)
            ):

                # get virtual cell at this location, which should not have
                # a cell yet
                virtual_cell = virtual_rows[row_idx + row_offset][
                    col_idx + col_offset
                ]
                assert not virtual_cell.cell_is_set

                # get origin virtual cell
                origin_cell = virtual_rows[row_idx][col_idx]

                # set this cell
                virtual_cell.set_cell(cell, row_offset, col_offset, origin_cell)

        # validate: ensure each virtual cell got set
        for row_idx, col_idx in itertools.product(
            range(row_count), range(col_count)
        ):
            assert virtual_rows[row_idx][col_idx].cell_is_set

        # set content lines
        for row in virtual_rows:
            for virtual_cell in row:

                if not virtual_cell.is_spanned:
                    # no spanned cells, just set content
                    virtual_cell.set_content(
                        virtual_cell.cell._get_content(
                            self.flavor, width=virtual_cell.effective_width
                        )
                    )
                    continue

                elif not virtual_cell.is_origin:
                    # spanned cells, but this is not origin cell
                    continue

                # allocate content for cell and all spanned cells
                width = self.__get_spanned_width(row, virtual_cell)
                self.__allocate_content(virtual_rows, virtual_cell, width)

        # validate: ensure contents got set
        for row_idx, col_idx in itertools.product(
            range(row_count), range(col_count)
        ):
            assert virtual_rows[row_idx][col_idx].content_is_set

        return virtual_rows

    def __get_spanned_width(
        self, row: list[VirtualCell], virtual_cell: VirtualCell
    ):
        # add up raw widths from all spanned columns
        width: int = 0
        for col_offset in range(virtual_cell.cell.cspan):
            width += row[virtual_cell.col_idx + col_offset].effective_width
        return width

    def __get_row_height(self, row: list[VirtualCell]) -> int | None:
        """
        Get max height (number of lines) of this row, based only on cells which
        don't span multiple rows. Returns `None` if there are no such cells
        constraining the height.
        """

        # collect cells which don't span rows
        non_rspan_cells = [cell for cell in row if cell.cell.rspan == 1]

        if not len(non_rspan_cells):
            # all cells have spanned rows
            return None

        # list of row heights
        heights: list[int] = []

        for cell in non_rspan_cells:

            if not cell.is_origin:
                # skip if not origin cell, we would have already counted it
                continue
            elif cell.content_is_set:
                # if already have content, get height
                heights.append(len(cell.lines))
                continue

            # get total width of this cell and add height of resulting content
            # - content for spanned cells has not been set yet
            width = self.__get_spanned_width(row, cell)
            heights.append(
                len(cell.cell._get_content(self.flavor, width=width))
            )

        return max(heights) if len(heights) else None

    def __allocate_content(
        self,
        rows: list[list[VirtualCell]],
        virtual_cell: VirtualCell,
        width: int,
    ):
        """
        Allocate the content for this cell across all the rows/columns it
        spans, wrapping content at the given width.
        """
        assert virtual_cell.row_idx + virtual_cell.cell.rspan <= len(rows)

        # get content, possibly wrapping at width of all spanned cells
        # - content is cached, so need to make copy
        content = virtual_cell.cell._get_content(
            self.flavor, width=width
        ).copy()

        # traverse each virtual row
        for row_offset in range(virtual_cell.cell.rspan):

            # select this row
            row = rows[virtual_cell.row_idx + row_offset]

            # select subset of row which is spanned
            cells = row[
                virtual_cell.col_idx : virtual_cell.col_idx
                + virtual_cell.cell.cspan
            ]

            # get list of widths for each spanned cell
            cell_widths = [cell.effective_width for cell in cells]

            # create list of lines per cell in this spanned row
            cell_lines: list[list[str]] = [
                [] for _ in range(virtual_cell.cell.cspan)
            ]

            # get max height of this row
            max_height = self.__get_row_height(row)

            # loop over lines until expected height, if there is one
            line_idx = 0
            last_row = row_offset == virtual_cell.cell.rspan - 1

            while (line_idx < (max_height or 1)) or (len(content) and last_row):
                line_idx += 1

                # consume next line of content
                line = content.pop(0) if len(content) else ""

                # divide this line among each cell in row
                segs = _split_line(line, cell_widths)

                # append segments to each list of lines
                assert len(cell_lines) == len(segs)
                for lines, seg in zip(cell_lines, segs):
                    lines.append(seg)

                if len(content) == 0:
                    # consumed all content
                    break

            # set content for each cell in row
            assert len(cells) == len(cell_lines)
            for cell, lines in zip(cells, cell_lines):
                cell.set_content(lines)

            # if this is isn't the last row, set dangling line
            if row_offset < (virtual_cell.cell.rspan - 1):

                segs: list[str]

                if len(content):
                    # still content, so consume the next line
                    segs = _split_line(content.pop(0), cell_widths)
                else:
                    # reached end of content, use empty strings for segments
                    segs = [""] * len(cell_widths)

                # set dangling lines
                assert len(cells) == len(segs)
                for cell, seg in zip(cells, segs):
                    cell.set_dangling_line(seg)


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
