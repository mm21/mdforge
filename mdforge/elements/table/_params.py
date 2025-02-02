"""
Encapsulates table params, universal for all flavors.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Iterable

from .cell import VALID_ALIGNS, AlignType, Cell

__all__ = [
    "TableParams",
]


@dataclass(frozen=True)
class TableParams:
    """
    Parameters from user, applicable to all table variants.
    """

    content_rows: list[list[Cell]]
    """
    List of rows, each of which is a list of cells.
    """

    header_rows: list[list[Cell]] | None
    """
    Optional header. May contain multiple rows for `BlockTable` only.
    """

    footer_rows: list[list[Cell]] | None
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

    @property
    def content_row_count(self) -> int:
        """
        Get number of content rows.
        """
        return len(self.content_rows)

    @cached_property
    def header_row_count(self) -> int:
        """
        Get number of header rows.
        """
        return len(self.header_rows) if self.header_rows else 0

    @cached_property
    def footer_row_count(self) -> int:
        """
        Get number of footer rows.
        """
        return len(self.footer_rows) if self.footer_rows else 0

    @cached_property
    def col_count(self) -> int:
        """
        Get number of columns.
        """
        return _get_col_count(self.__effective_rows)

    @cached_property
    def col_aligns(self) -> list[AlignType]:
        """
        Get column alignments.
        """
        match self.align:
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
                assert self.align is None
                aligns = ["default"] * self.col_count
        return aligns

    @cached_property
    def __effective_rows(self) -> list[list[Cell]]:
        """
        Get overall rows, including any header / footer.
        """
        return (
            (self.header_rows or [])
            + self.content_rows
            + (self.footer_rows or [])
        )


def _get_col_count(rows: list[list[Cell]]) -> tuple[int, int]:
    """
    Get effective columns of the provided matrix, accounting for any
    merged cells.
    """

    if not rows:
        return 0

    # column counts per row
    col_counts: list[int] = []

    def add_col_count(index: int, val: int):
        """
        Add value at the given row index, inserting elements as needed.
        """
        nonlocal col_counts
        if index >= len(col_counts):
            col_counts += [0] * (index - len(col_counts) + 1)
        col_counts[index] += val

    # get col counts
    for row_idx, row in enumerate(rows):
        for cell in row:
            # add columns for each row, including spanned ones
            for row_offset in range(cell.rspan):
                add_col_count(row_idx + row_offset, cell.cspan)

    # verify consistency
    assert len(rows) == len(col_counts)
    for row_idx, col_count in enumerate(col_counts):
        assert (
            col_count == col_counts[row_idx - 1]
        ), f"Inconsistent column counts: row {row_idx}={col_count}, row {row_idx-1}={col_counts[row_idx-1]}"

    return col_counts[0]
