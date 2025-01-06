"""
Table element.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Literal, cast

from ..element import BaseElement
from ..types import FlavorType

__all__ = [
    "CellType",
    "AlignType",
    "InlineTable",
    "BlockTable",
    "BaseTable",
]

type CellType = str | BaseElement | Cell
type RowType = list[CellType]
type AlignType = Literal["left", "center", "right"]


@dataclass
class Cell:

    content: str | BaseElement
    """
    Cell content.
    """

    rspan: int | None = None
    """
    Row span, only valid for `BlockTable`.
    """

    cspan: int | None = None
    """
    Column span, only valid for `BlockTable`.
    """

    @classmethod
    def _normalize(cls, cell: CellType) -> Cell:
        if isinstance(cell, Cell):
            return cell
        else:
            assert isinstance(cell, (str, BaseElement))
            return Cell(cell)


@dataclass
class BaseTable(BaseElement):

    _rows: list[list[Cell]]
    """
    Normalized list of rows, each of which is a list of cells.
    """

    _header: list[list[Cell]] | None
    """
    Optional header. May contain multiple rows for `BlockTable` only.
    """

    _footer: list[list[Cell]] | None
    """
    Optional footer. May contain multiple rows for `BlockTable` only.
    """

    _align: AlignType | list[AlignType] | None
    """
    Optional alignment for each column.
    """

    _widths: list[int] | None
    """
    If provided, generated cells are sized to that number of characters
    by padding or wrapping lines. Otherwise, widths are as small as possible.

    Useful to generate consistently-sized tables for varying content length.
    """

    _caption: str | None
    """
    Table caption.
    """

    _clean: bool
    """
    Whether to remove top and bottom rules for this table.
    """

    _col_count: int
    """
    Number of columns, including any header and footer.
    """

    _row_count: int
    """
    Number of rows, including any header and footer.
    """

    def __init__(
        self,
        rows: list[RowType],
        header: RowType | list[RowType] | None = None,
        footer: RowType | list[RowType] | None = None,
        align: AlignType | list[AlignType] | None = None,
        widths: list[int] | None = None,
        caption: str | None = None,
        clean: bool = False,
    ):
        self._rows = self.__normalize_rows(rows)
        self._header = self.__normalize_rows(header) if header else None
        self._footer = self.__normalize_rows(footer) if footer else None
        self._align = align
        self._widths = widths
        self._caption = caption
        self._clean = clean

        self._col_count, self._row_count = self.__get_dims(
            (self._header or []) + self._rows + (self._footer or [])
        )

        print(f"--- got size: {self._size}")

    @property
    def _size(self) -> tuple[int, int]:
        return self._col_count, self._row_count

    def _render_header(self) -> Generator[str, None, None]:
        """
        Yield lines for header.
        """
        yield ""

    def _render_rows(self) -> Generator[str, None, None]:
        """
        Yield lines for rows.
        """
        yield ""

    def _render_footer(self) -> Generator[str, None, None]:
        """
        Yield lines for footer.
        """
        yield ""

    # TODO
    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:

        yield from self._render_header()
        yield from self._render_rows()
        yield from self._render_footer()

        yield f"Table: {type(self).__name__}, rows: {self._rows}"

    def __normalize_rows(
        self, rows: RowType | list[RowType]
    ) -> list[list[Cell]]:
        """
        Normalize given rows to a list of lists of cells.
        """
        assert len(rows)
        rows_ = cast(
            list[RowType], [rows] if isinstance(rows[0], str) else rows
        )
        rows_norm: list[list[Cell]] = []
        for row in rows_:
            rows_norm.append([Cell._normalize(cell) for cell in row])
        return rows_norm

    def __transpose(self, rows: list[list[Cell]]) -> list[list[Cell | None]]:

        cols_max = max(len(row) for row in rows)
        rows_pad: list[list[Cell]] = [
            row + [None] * (cols_max - len(row)) for row in rows
        ]

        return cast(list[list[Cell]], list(map(list, zip(*rows_pad))))

    def __get_dims(self, rows: list[list[Cell]]) -> tuple[int, int]:
        """
        Get effective dimensions of provided content (header or rows),
        accounting for any merged cells.
        """
        cols = self.__transpose(rows)
        return self.__get_col_count(
            rows, "cspan", "column"
        ), self.__get_col_count(cols, "rspan", "row")

    def __get_col_count(
        self, rows: list[list[Cell | None]], span_attr: str, dim: str
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

        assert len(col_counts)

        # validate
        for i in range(len(col_counts)):
            assert (
                col_counts[i] == col_counts[i - 1]
            ), f"Inconsistent {dim} counts: {col_counts}"

        return col_counts[0]


class InlineTable(BaseTable):
    """
    Table which only supports inline elements. Maps to a `multiline` table
    for `pandoc` flavor.

    For example:

    ```
    -------------------------------------------------------------
     Centered   Default           Right Left
      Header    Aligned         Aligned Aligned
    ----------- ------- --------------- -------------------------
       First    row                12.0 Example of a row that
                                        spans multiple lines.

      Second    row                 5.0 Here's another one. Note
                                        the blank line between
                                        rows.
    -------------------------------------------------------------
    ```
    """


class BlockTable(BaseTable):
    """
    Table which supports block elements like paragraphs in addition to inline
    elements. Maps to a `grid` table for `pandoc` flavor.

    For example:
    ```
    +---------------------+-----------------------+
    | Location            | Temperature 1961-1990 |
    |                     | in degree Celsius     |
    |                     +-------+-------+-------+
    |                     | min   | mean  | max   |
    +=====================+=======+=======+=======+
    | Antarctica          | -89.2 | N/A   | 19.8  |
    +---------------------+-------+-------+-------+
    | Earth               | -89.2 | 14    | 56.7  |
    +---------------------+-------+-------+-------+
    ```
    """
