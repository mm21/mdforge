"""
Encapsulates table params, universal for all flavors.
"""

from dataclasses import dataclass
from functools import cached_property

from ._utils import get_dims
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
    List of rows, each of which is a list of cells.
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
    def effective_dims(self) -> tuple[int, int]:
        """
        Get overall dimensions, including any header / footer.
        """
        return get_dims(self.effective_rows)

    @cached_property
    def effective_rows(self) -> list[list[Cell]]:
        """
        Get overall rows, including any header / footer.
        """
        return (self.header or []) + self.rows + (self.footer or [])
