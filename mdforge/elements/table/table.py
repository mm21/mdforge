"""
Table element.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache, cached_property
from typing import Generator, Iterable, Literal, cast

from ...element import BaseElement
from ...types import FlavorType
from ._clean import get_clean_end, get_clean_start
from ._config import SectionConfig, TableConfig
from ._configs import lookup_config

__all__ = [
    "Table",
    "Cell",
    "CellType",
    "RowType",
    "AlignType",
]


CLEAN_START = get_clean_start()
"""
List of code lines to backup latex commands.
"""

CLEAN_END = get_clean_end()
"""
List of code lines to restore latex commands.
"""

type CellType = str | BaseElement | Cell
type RowType = list[CellType]
type AlignType = Literal["left", "center", "right", "default"]


@dataclass(frozen=True)
class Cell:

    content: str | list[str] | BaseElement
    """
    Cell content.
    """

    rspan: int | None = None
    """
    Row span, only valid for `block=True`.
    """

    cspan: int | None = None
    """
    Column span, only valid for `block=True`.
    """

    @classmethod
    def _normalize(cls, cell: CellType) -> Cell:
        if isinstance(cell, Cell):
            return cell
        else:
            assert isinstance(cell, (str, BaseElement))
            return Cell(cell)

    @cache
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


class Table(BaseElement):

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

    _block: bool
    """
    Whether table should support block content such as paragraphs and lists.
    """

    _clean: bool
    """
    Whether to omit top and bottom lines for this table.
    """

    def __init__(
        self,
        rows: list[RowType],
        header: RowType | list[RowType] | None = None,
        footer: RowType | list[RowType] | None = None,
        align: AlignType | list[AlignType] | None = None,
        widths: list[int] | None = None,
        caption: str | None = None,
        block: bool = False,
        clean: bool = False,
    ):
        self._rows = self.__normalize_rows(rows)
        self._header = self.__normalize_rows(header) if header else None
        self._footer = self.__normalize_rows(footer) if footer else None
        self._align = align
        self._widths = widths
        self._caption = caption
        self._block = block
        self._clean = clean

    @property
    def _col_count(self) -> int:
        """
        Get number of columns.
        """
        return self._effective_dims[0]

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

    @cache
    def _get_col_widths(
        self, flavor: FlavorType, config: TableConfig
    ) -> list[int]:
        """
        Get widths of the content in each column.
        """

        def get_raw_widths():
            if self._widths:
                return self._widths
            else:
                return self.__get_widths(self._effective_rows, flavor)

        raw_widths = get_raw_widths()

        if config.cell_sep is not None or self._header is None:
            # if cell separators or no header, don't need to adjust widths
            return raw_widths

        # if no cell separators, allow 1 extra char in the header to ensure
        # widths are wide enough for content to be aligned via spaces
        header_widths = self._get_header_widths(flavor)

        return [
            max(raw, header + 1)
            for raw, header in zip(raw_widths, header_widths)
        ]

    @cache
    def _get_header_widths(self, flavor: FlavorType) -> list[int]:

        assert self._header is not None
        return self.__get_widths(self._header, flavor)

    def __get_widths(self, rows: list[list[Cell]], flavor: FlavorType):
        """
        Get widths of the provided rows.
        """
        widths: list[int] = [0] * self._col_count
        for row in rows:
            assert len(row) == len(widths)
            for i, cell in enumerate(row):
                widths[i] = max(
                    widths[i],
                    *(len(line) for line in cell._get_content(flavor)),
                )
        return widths

    def _render_rows(
        self,
        rows: list[list[Cell]],
        flavor: FlavorType,
        config: TableConfig,
        section: SectionConfig,
        include_upper: bool = False,
        include_lower: bool = False,
    ) -> Generator[str, None, None]:
        """
        Yield lines for rows, separated by separator (between rows) and
        optional upper/lower separators.
        """

        widths = self._get_col_widths(flavor, config)

        sep_line = section.sep.get_line(widths, config)

        if include_upper:
            sep = section.upper_sep or section.sep
            yield sep.get_line(widths, config)

        for row_idx, row in enumerate(rows):

            row_lines = [cell._get_content(flavor) for cell in row]
            max_lines = max(len(lines) for lines in row_lines)

            for line_idx in range(max_lines):

                # segments for this row line
                segs: list[str] = []

                for cell_idx, cell_lines in enumerate(row_lines):
                    content = (
                        cell_lines[line_idx]
                        if line_idx < len(cell_lines)
                        else ""
                    )

                    # TODO: handle alignment

                    leading_space = " " if config.cell_sep is not None else ""

                    if config.cell_sep is None:
                        # no cell separator
                        trailing_space = (
                            "  " if cell_idx != len(row_lines) - 1 else ""
                        )
                    else:
                        # have cell separator, e.g. "|"
                        trailing_space = " "

                    segs.append(
                        f"{leading_space}{content:<{widths[cell_idx]}}{trailing_space}"
                    )

                cell_sep = config.cell_sep or ""
                yield cell_sep + cell_sep.join(segs) + cell_sep

            if row_idx != len(rows) - 1:
                yield sep_line

        if include_lower:
            sep = section.lower_sep or section.sep
            yield sep.get_line(widths, config)

    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        print(f"Table: {type(self).__name__}, rows: {self._rows}")

        config = lookup_config(flavor, self._block)

        if self._clean:
            yield from CLEAN_START

        if self._header:
            yield from self._render_rows(
                self._header,
                flavor,
                config,
                config.header,
                include_upper=True,
                include_lower=True,
            )

        yield from self._render_rows(
            self._rows,
            flavor,
            config,
            config.content,
            include_upper=self._header is None,
            include_lower=self._footer is None,
        )

        if self._footer:
            yield from self._render_rows(
                self._footer,
                flavor,
                config,
                config.footer,
                include_upper=True,
                include_lower=True,
            )

        if self._clean:
            yield from CLEAN_END

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
