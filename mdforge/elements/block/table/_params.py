"""
Encapsulates table params, universal for all flavors.
"""

import itertools
from dataclasses import dataclass
from functools import cached_property
from typing import Iterable, cast

from ....types import VALID_ALIGNS, AlignType
from .cell import Cell

__all__ = [
    "TableParams",
]


@dataclass(frozen=True, kw_only=True)
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

    widths: list[int] | None
    """
    If provided, generated cells are sized to that number of characters
    by padding or wrapping lines. Otherwise, widths are as small as possible.

    Useful to generate consistently-sized tables for varying content length.
    """

    widths_pct: list[int] | None
    """
    Widths as percents.
    """

    caption: str | None
    """
    Table caption.
    """

    block: bool
    """
    Whether table should support block content such as paragraphs and lists.
    """

    loose: bool
    """
    Whether cell content should always be wrapped in a paragraph in the
    rendered output (HTML only). Ensures consistent padding if there are
    any cells containing block content.
    """

    col_count: int
    """
    Number of columns.
    """

    @cached_property
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
    def effective_rows(self) -> list[list[Cell]]:
        """
        Get overall rows, including any header / footer.
        """
        return (
            (self.header_rows or [])
            + self.content_rows
            + (self.footer_rows or [])
        )

    @cached_property
    def norm_content_rows(self) -> list[list[Cell]]:
        """
        Get normalized content rows.
        """
        return self.__normalize_rows(self.content_rows)

    @cached_property
    def norm_header_rows(self) -> list[list[Cell]]:
        """
        Get normalized header rows.
        """
        return (
            self.__normalize_rows(self.header_rows)
            if self.header_rows
            else None
        )

    @cached_property
    def norm_footer_rows(self) -> list[list[Cell]]:
        """
        Get normalized footer rows.
        """
        return (
            self.__normalize_rows(self.footer_rows)
            if self.footer_rows
            else None
        )

    @cached_property
    def norm_effective_rows(self) -> list[list[Cell]]:
        """
        Get normalized overall rows, including any header / footer.
        """
        return (
            (self.norm_header_rows or [])
            + self.norm_content_rows
            + (self.norm_footer_rows or [])
        )

    def __normalize_rows(self, rows: list[list[Cell]]) -> list[list[Cell]]:
        """
        Normalize input, accounting for cell spans to create evenly sized rows.
        """

        row_count, col_count = len(rows), self.col_count

        # pre-allocate rows
        norm_rows: list[list[Cell | None]] = [
            [None for _ in range(col_count)] for _ in range(row_count)
        ]

        for row_idx, row in enumerate(rows):
            for cell in row:

                # advance to column with next available cell
                col_idx = 0
                for col_idx in range(col_count):
                    if norm_rows[row_idx][col_idx] is None:
                        break
                assert col_idx < col_count

                # traverse this cell along with all spanned ones
                for row_offset, col_offset in itertools.product(
                    range(cell._rspan), range(cell._cspan)
                ):
                    # should not be set yet
                    assert (
                        norm_rows[row_idx + row_offset][col_idx + col_offset]
                        is None
                    )

                    # set this cell
                    norm_rows[row_idx + row_offset][col_idx + col_offset] = cell

                col_idx += cell._cspan

        # validate: ensure each cell got set
        for row_idx, col_idx in itertools.product(
            range(row_count), range(col_count)
        ):
            assert isinstance(norm_rows[row_idx][col_idx], Cell)

        return cast(list[list[Cell]], norm_rows)
