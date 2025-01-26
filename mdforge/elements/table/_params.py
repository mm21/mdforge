"""
Encapsulates table params, universal for all flavors.
"""

from dataclasses import dataclass
from functools import cached_property

from .cell import AlignType, Cell

__all__ = [
    "TableParams",
]


@dataclass(frozen=True)
class TableParams:
    """
    Parameters from user, applicable to all table variants.
    """

    rows: list[list[Cell]]
    """
    Normalized list of rows, each of which is a list of cells.
    """

    header: list[list[Cell]] | None
    """
    Optional header. May contain multiple rows for `BlockTable` only.
    """

    footer: list[list[Cell]] | None
    """
    Optional footer. May contain multiple rows for `BlockTable` only.
    """

    align: AlignType | list[AlignType] | None
    """
    Optional alignment for each column, single alignmen to apply to all columns.
    """

    widths: list[int | None] | None
    """
    If provided, generated cells are sized to that number of characters
    by padding or wrapping lines. Otherwise, widths are as small as possible.

    Useful to generate consistently-sized tables for varying content length.
    """

    caption: str | None
    """
    Table caption.
    """

    block: bool
    """
    Whether table should support block content such as paragraphs and lists.
    """

    clean: bool
    """
    Whether to omit top and bottom lines for this table.
    """

    def __hash__(self) -> int:
        """
        Table params are considered immutable, even though they contain
        mutable types (lists). This method is implemented to enable caching of
        values derived from the user inputs.
        """
        return id(self)

    @cached_property
    def effective_rows(self) -> list[list[Cell]]:
        """
        Get all rows, including any header / footer.
        """
        return (self.header or []) + self.rows + (self.footer or [])

    @cached_property
    def effective_dims(self) -> tuple[int, int]:
        """
        Get overall dimensions, including any header / footer.
        """
        return self.__get_dims(self.effective_rows)

    def __get_dims(self, rows: list[list[Cell]]) -> tuple[int, int]:
        """
        Get effective dimensions of provided content (header or rows),
        accounting for any merged cells.
        """

        assert len(rows)
        for row in rows:
            assert len(row)

        col_count: int
        row_count: int

        col_counts: list[int] = []  # counts per row
        row_counts: list[int] = []  # counts per column

        def add_at(counts: list[int], index: int, val: int):
            if index >= len(counts):
                counts += [0] * (index - len(counts) + 1)

            counts[index] += val

        # get col counts
        for row_idx, row in enumerate(rows):

            # add columns for this row, accounting for spanned columns
            add_at(col_counts, row_idx, sum(cell.cspan or 1 for cell in row))

            # look ahead to account for spanned rows
            for cell in row:
                if cell.rspan:
                    for i in range(1, cell.rspan):
                        add_at(col_counts, row_idx + i, cell.cspan or 1)

        # verify consistency
        assert len(col_counts)
        assert all(
            col_count == col_counts[i - 1]
            for i, col_count in enumerate(col_counts)
        )
        col_count = col_counts[0]

        # get row counts
        # TODO: handle spanned columns
        for col_idx in range(col_count):
            row_count = 0
            for row in rows:
                if col_idx < len(row):
                    row_count += row[col_idx].rspan or 1
            row_counts.append(row_count)

        # verify consistency
        assert len(row_counts)
        assert all(
            row_count == row_counts[i - 1]
            for i, row_count in enumerate(row_counts)
        )
        row_count = row_counts[0]

        return col_count, row_count
