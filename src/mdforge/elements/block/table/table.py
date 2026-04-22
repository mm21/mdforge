"""
Table element.
"""

from __future__ import annotations

from typing import Any, Generator, Iterable, cast

from mdforge._norm import CoerceSpec, norm_obj

from ....element import BaseBlockElement, BaseElement
from ....exceptions import ValidationError
from ....types import AlignType, FlavorType
from ._flavors.flavors import create_render_context
from ._params import TableParams
from .cell import Cell, RowType

__all__ = [
    "Table",
]

VALID_CELL_TYPES = (str, BaseElement, Cell)


class Table(BaseBlockElement):

    _params: TableParams
    """
    Immutable table parameters as passed by user.
    """

    def __init__(
        self,
        rows: Iterable[RowType],
        header: RowType | Iterable[RowType] | None = None,
        footer: RowType | Iterable[RowType] | None = None,
        align: AlignType | Iterable[AlignType] | None = None,
        widths: Iterable[int] | None = None,
        widths_pct: Iterable[int] | None = None,
        caption: str | None = None,
        block: bool = False,
        loose: bool = False,
    ):
        """
        :param rows: Content rows
        :param header: Header row(s)
        :param footer: Footer row(s)
        :param align: Column alignment(s)
        :param widths: Absolute column widths in characters, mutually exclusive with `widths_pct`
        :param widths_pct: Column widths in percents, mutually exclusive with `widths`
        :param caption: Caption, if supported by flavor
        :param block: Whether cells can have block content
        :param loose: Whether to insert explicit paragraph tags for consistency with cells containing block elements
        """

        if widths is not None and widths_pct is not None:
            raise ValidationError(
                f"Ambiguous widths: cannot pass both widths={widths} and widths_pct={widths_pct}"
            )

        widths_norm = list(widths) if widths else None
        widths_pct_norm = list(widths_pct) if widths_pct else None

        if widths_pct_norm is not None:
            if (total := sum(widths_pct_norm)) != 100:
                raise ValidationError(
                    f"Width percents must add to 100, got {total}: {widths_pct_norm}"
                )

            if any(width_pct == 0 for width_pct in widths_pct_norm):
                raise ValidationError(
                    f"Width percents must be nonzero, got {widths_pct_norm}"
                )

        if loose and not block:
            raise ValidationError(f"Table with loose=True requires block=True")

        content_rows = _normalize_cells(rows)
        header_rows = _normalize_cells(header) if header else None
        footer_rows = _normalize_cells(footer) if footer else None
        col_count = _get_col_count(
            content_rows + (header_rows or []) + (footer_rows or [])
        )

        def validate_widths(
            var: list[int],
            var_name: str,
        ):
            if len(var) != col_count:
                raise ValidationError(
                    f"{var_name}={var} does not match col_count={col_count}"
                )
            if not all(isinstance(width, int) for width in var):
                raise ValidationError(
                    f"{var_name}={var} must be passed as list of int"
                )

        if widths_norm is not None:
            validate_widths(widths_norm, "widths")

        if widths_pct_norm is not None:
            validate_widths(widths_pct_norm, "widths_pct")

        self._params = TableParams(
            content_rows=content_rows,
            header_rows=header_rows,
            footer_rows=footer_rows,
            align=align,
            widths=widths_norm,
            widths_pct=widths_pct_norm,
            caption=caption,
            block=block,
            loose=loose,
            col_count=col_count,
        )

        # ensure content is valid given params
        for row in self._params.effective_rows:
            for cell in row:
                if not block and cell._is_block:
                    raise ValidationError(
                        f"Inline-only table contains a block element: {cell._element}"
                    )

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:

        # create render context
        context = create_render_context(
            flavor, self._params, self._params.block
        )

        # start comment, required to disambiguate table caption in case of
        # back-to-back tables (caption can be before or after table)

        descs: list[str] = []

        if align := self._params.align:
            descs.append(f"align={align}")
        if widths := self._params.widths:
            descs.append(f"widths={widths}")
        if widths_pct := self._params.widths_pct:
            descs.append(f"widths_pct={widths_pct}")
        if block := self._params.block:
            descs.append(f"block={block}")
        if loose := self._params.loose:
            descs.append(f"loose={loose}")

        desc = f": {', '.join(descs)}" if descs else ""
        yield f"<!-- table start{desc} -->\n"

        # render caption
        if caption := self._params.caption:
            yield f": {caption}\n"

        # render based on variant
        yield from context.render()

        yield "\n<!-- table end -->"

    def _get_pandoc_extensions(self) -> set[str]:
        table_ext = (
            {"grid_tables"} if self._params.block else {"multiline_tables"}
        )
        caption_ext = {"table_captions"} if self._params.caption else set()
        return table_ext | caption_ext | super()._get_pandoc_extensions()


def _normalize_cells(rows: RowType | Iterable[RowType]) -> list[list[Cell]]:
    """
    Normalize given rows to a list of lists of cells.
    """

    if not (isinstance(rows, Iterable) and len(rows)):
        raise ValidationError(f"Invalid row specification: {rows}")

    rows_list = list(rows)

    # normalize to list of lists
    rows_lists: list[list[Any]]

    if all(isinstance(cell, VALID_CELL_TYPES) for cell in rows_list):
        # have a list of valid cell types
        rows_lists = cast(list[list[Any]], [rows_list])
    elif all(isinstance(row, Iterable) for row in rows_list):
        # have a list of iterables
        rows_lists = cast(list[list[Any]], rows_list)
    else:
        raise ValidationError(f"Invalid row or iterable of rows: {rows_list}")

    # normalize to list of lists of cells
    rows_norm: list[list[Cell]] = []
    for row in rows_lists:
        rows_norm.append(
            [
                norm_obj(cell, Cell, CoerceSpec(Cell, (str, BaseElement)))
                for cell in row
            ]
        )

    return rows_norm


def _get_col_count(rows: list[list[Cell]]) -> int:
    """
    Get effective columns of the provided matrix, accounting for any
    merged cells.
    """

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
            for row_offset in range(cell._rspan):
                add_col_count(row_idx + row_offset, cell._cspan)

    # verify consistency
    assert len(rows) == len(col_counts)
    for row_idx, col_count in enumerate(col_counts):
        if col_count != col_counts[row_idx - 1]:
            raise ValidationError(
                f"Inconsistent column counts: row {row_idx}={col_count}, row {row_idx-1}={col_counts[row_idx-1]}"
            )

    return col_counts[0]
