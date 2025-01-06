"""
Table element.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Generator, Iterable, Literal, cast

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

    content: str | list[str] | BaseElement
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

    @lru_cache()
    def _get_content(self, flavor: FlavorType) -> list[str]:
        """
        Get this cell's content as a list of strings.
        """
        content = self.content

        if isinstance(content, str):
            return content.split("\n")
        elif isinstance(content, Iterable):
            assert all(isinstance(line, str) for line in content)
            return list(content)

        assert isinstance(content, BaseElement)
        return list(content._render_element(flavor))


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
    r"""
    Whether to remove top and bottom rules for this table.

    Inserts the following before tables:

    ```
    \let\oldtoprule\toprule
    \renewcommand{\toprule}{}
    \let\oldbottomrule\bottomrule
    \renewcommand{\bottomrule}{}
    \let\oldendfoot\endfoot
    \renewcommand{\endfoot}{}
    \let\oldendlastfoot\endlastfoot
    \renewcommand{\endlastfoot}{}
    ```

    And after tables:

    ```
    \let\toprule\oldtoprule
    \let\bottomrule\oldbottomrule
    \let\endfoot\oldendfoot
    \let\endlastfoot\oldendlastfoot
    ```
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

    @property
    def _col_count(self) -> int:
        """
        Get number of columns.
        """
        return self._effective_dims([0])

    @property
    def _effective_rows(self) -> list[list[Cell]]:
        """
        Get all rows, including any header / footer.
        """
        return (self._header or []) + self._rows + (self._footer or [])

    @cached_property
    def _row_count(self) -> tuple[int, int]:
        """
        Get number of rows.
        """
        return self.__get_dims(self._rows)[1]

    @cached_property
    def _header_row_count(self) -> tuple[int, int]:
        """
        Get number of header rows.
        """
        assert self._header is not None
        return self.__get_dims(self._header)[1]

    @cached_property
    def _footer_row_count(self) -> tuple[int, int]:
        """
        Get number of footer rows.
        """
        assert self._footer is not None
        return self.__get_dims(self._footer)

    @cached_property
    def _effective_dims(self) -> tuple[int, int]:
        """
        Get overall dimensions, including any header / footer.
        """
        return self.__get_dims(self._effective_rows)

    @cached_property
    def _get_col_widths(self, flavor: FlavorType) -> list[int]:
        """
        Get widths of the content of each column.
        """

        if self._widths:
            return self._widths

        widths: list[int] = [0] * self._col_count

        for row in self._effective_rows:
            assert len(row) == len(widths)
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell._get_content(flavor)))

        return widths

    def _render_header(self, flavor: FlavorType) -> Generator[str, None, None]:
        """
        Yield lines for header.
        """
        # TODO
        yield ""

    def _render_rows(self, flavor: FlavorType) -> Generator[str, None, None]:
        """
        Yield lines for rows.
        """
        # TODO
        yield ""

    def _render_footer(self, flavor: FlavorType) -> Generator[str, None, None]:
        """
        Yield lines for footer.
        """
        # TODO
        yield ""

    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        print(f"Table: {type(self).__name__}, rows: {self._rows}")

        yield from self._render_header(flavor)
        yield from self._render_rows(flavor)
        yield from self._render_footer(flavor)

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

    ----------- ------- --------------- -------------------------
       First    row                12.0 Example of a row that
                                        spans multiple lines.

      Second    row                 5.0 Here's another one. Note
                                        the blank line between
                                        rows.
    ----------- ------- --------------- -------------------------
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
    +=====================+=======+=======+=======+
    | Average             | -89.2 | N/A   | 38.25 |
    +=====================+=======+=======+=======+

    +---------------+---------------+--------------------+
    | Right         | Left          | Centered           |
    +==============:+:==============+:==================:+
    | Bananas       | $1.34         | built-in wrapper   |
    +---------------+---------------+--------------------+

    +--------------:+:--------------+:------------------:+
    | Right         | Left          | Centered           |
    +---------------+---------------+--------------------+
    ```
    """
