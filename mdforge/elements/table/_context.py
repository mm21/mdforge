"""
Encapsulates context for rendering tables.
"""

import itertools
from dataclasses import dataclass
from functools import cached_property
from typing import Iterable

from ...types import FlavorType
from ._flavors.flavor import BaseTableVariant
from ._params import TableParams
from .cell import VALID_ALIGNS, AlignType, Cell, VirtualCell


@dataclass(frozen=True)
class RenderContext:

    flavor: FlavorType
    variant: BaseTableVariant
    params: TableParams

    @property
    def row_count(self) -> int:
        """
        Get number of rows.
        """
        return self.params.effective_dims[0]

    @property
    def col_count(self) -> int:
        """
        Get number of columns.
        """
        return self.params.effective_dims[1]

    @cached_property
    def col_widths(self) -> list[int]:
        """
        Get normalized widths based on params and variant.
        """
        content_widths = self.__get_content_widths()
        assert len(content_widths) == self.col_count

        if self.params.widths:

            # normalize provided widths in case any are None, indicating to
            # use the content width

            assert len(self.params.widths) == self.col_count
            widths: list[int] = []

            for param_width, content_width in zip(
                self.params.widths, content_widths
            ):
                widths.append(param_width or content_width)

            return widths
        else:
            return content_widths

    @cached_property
    def col_aligns(self) -> list[AlignType]:
        """
        Get column alignments.
        """
        match self.params.align:
            case str() as align:
                # single alignment given
                assert align in VALID_ALIGNS
                aligns = [align] * self.col_count
            case iterable if isinstance(iterable, Iterable):
                # alignments per column given
                assert len(iterable) == self.col_count
                assert all(a in VALID_ALIGNS for a in iterable)
                aligns = iterable
            case _:
                # no alignment given
                assert self.params.align is None
                aligns = ["default"] * self.col_count
        return aligns

    def wrap_rows(
        self, rows: list[list[Cell]], row_count: int, col_count: int
    ) -> list[list[VirtualCell]]:
        """
        Normalize cells to wrapped cells, creating a consistently-sized
        matrix accounting for spanned cells.
        """

        wrapped_rows: list[list[VirtualCell]] = [
            [
                VirtualCell(self, row_idx, col_idx)
                for col_idx in range(col_count)
            ]
            for row_idx in range(row_count)
        ]

        for row_idx, row in enumerate(rows):
            for cell in row:

                # advance to column with next available cell
                for col_idx in range(self.col_count):
                    if not wrapped_rows[row_idx][col_idx].is_set:
                        break

                # traverse this cell along with all spanned ones
                for row_offset, col_offset in itertools.product(
                    range(cell.rspan), range(cell.cspan)
                ):

                    # get cell at this location, which should not have
                    # a wrapped cell yet
                    wrapped_cell = wrapped_rows[row_idx + row_offset][
                        col_idx + col_offset
                    ]
                    assert not wrapped_cell.is_set

                    wrapped_cell.set_cell(cell, row_offset, col_offset)

                col_idx += cell.cspan

        # validate: ensure each wrapped cell got set
        for row_idx, col_idx in itertools.product(
            range(row_count), range(col_count)
        ):
            wrapped_cell = wrapped_rows[row_idx][col_idx]
            assert wrapped_cell.is_set

        return wrapped_rows

    def __get_content_widths(self) -> list[int]:
        """
        Calculate column widths based on raw (non-wrapped) contents.
        """
        widths: list[int] = [0] * self.col_count
        wrapped_rows = self.wrap_rows(
            self.params.effective_rows, self.row_count, self.col_count
        )

        for row in wrapped_rows:
            assert len(row) == self.col_count

            for col_idx, cell in enumerate(row):
                content = list(cell.get_content())
                content_widths = [len(line) for line in content]

                widths[col_idx] = max([widths[col_idx]] + content_widths)

        return widths
