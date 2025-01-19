"""
Encapsulates table params, universal for all flavors.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Iterable, cast

from .cell import VALID_ALIGNS, AlignType, Cell

__all__ = [
    "TableParams",
]


@dataclass(frozen=True)
class TableParams:

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

    widths: list[int] | None
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

    def __hash__(self):
        return id(self)

    @cached_property
    def col_count(self) -> int:
        """
        Get number of columns.
        """
        return self.effective_dims[0]

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

    def __get_dims(self, rows: list[list[Cell]]) -> tuple[int, int]:
        """
        Get effective dimensions of provided content (header or rows),
        accounting for any merged cells.
        """

        def transpose(rows: list[list[Cell]]) -> list[list[Cell | None]]:
            cols_max = max(len(row) for row in rows)
            rows_pad: list[list[Cell | None]] = [
                row + [None] * (cols_max - len(row)) for row in rows
            ]
            return cast(
                list[list[Cell | None]], list(map(list, zip(*rows_pad)))
            )

        def get_col_count(
            rows: list[list[Cell | None]], span_attr: str, dim: str
        ) -> int:
            """
            Get effective number of columns, accounting for any merged cells.
            """
            col_counts: list[int] = []
            for row in rows:
                spans = [
                    getattr(cell, span_attr) or 1
                    for cell in row
                    if cell is not None
                ]
                col_counts.append(sum(spans))

            # validate
            assert len(col_counts)
            for i in range(len(col_counts)):
                assert (
                    col_counts[i] == col_counts[i - 1]
                ), f"Inconsistent {dim} counts: {col_counts}"

            return col_counts[0]

        cols = transpose(rows)
        return get_col_count(rows, "cspan", "column"), get_col_count(
            cols, "rspan", "row"
        )
