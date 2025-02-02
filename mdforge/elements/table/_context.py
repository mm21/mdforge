"""
Encapsulates context for rendering tables.
"""

import itertools
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
        return self.__get_virtual_rows(self.params.content_rows)

    @cached_property
    def virtual_header_rows(self) -> list[list[VirtualCell]] | None:
        """
        Get header rows as virtual cells.
        """
        if self.params.header_rows is None:
            return None
        return self.__get_virtual_rows(self.params.header_rows)

    @cached_property
    def virtual_footer_rows(self) -> list[list[VirtualCell]]:
        """
        Get effective rows as virtual cells.
        """
        if self.params.footer_rows is None:
            return None
        return self.__get_virtual_rows(self.params.footer_rows)

    @cached_property
    def virtual_effective_rows(self) -> list[list[VirtualCell]]:
        return (
            (self.virtual_header_rows or [])
            + self.virtual_content_rows
            + (self.virtual_footer_rows or [])
        )

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

        for col_idx, width in enumerate(param_widths):
            if width:
                # width passed from user
                widths.append(width)
            else:
                # get max width of this column
                widths.append(
                    max(
                        row[col_idx].raw_width
                        for row in self.virtual_effective_rows
                    )
                )

        return widths

    def __get_virtual_rows(
        self, rows: list[list[Cell]]
    ) -> list[list[VirtualCell]]:
        """
        Normalize cells to virtual cells, creating a consistently-sized
        matrix accounting for spanned cells.
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

        # traverse rows and populate virtual rows
        for row_idx, row in enumerate(rows):
            for cell in row:

                # advance to column with next available cell
                for col_idx in range(col_count):
                    if not virtual_rows[row_idx][col_idx].is_set:
                        break

                # traverse this cell along with all spanned ones
                for row_offset, col_offset in itertools.product(
                    range(cell.rspan), range(cell.cspan)
                ):

                    # get cell at this location, which should not have
                    # a wrapped cell yet
                    virtual_cell = virtual_rows[row_idx + row_offset][
                        col_idx + col_offset
                    ]
                    assert not virtual_cell.is_set

                    virtual_cell.set_cell(cell, row_offset, col_offset)

                col_idx += cell.cspan

        # validate: ensure each virtual cell got set
        for row_idx, col_idx in itertools.product(
            range(row_count), range(col_count)
        ):
            virtual_cell = virtual_rows[row_idx][col_idx]
            assert virtual_cell.is_set

        return virtual_rows
