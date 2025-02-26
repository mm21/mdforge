"""
Table element.
"""

from __future__ import annotations

from types import NoneType
from typing import Any, Generator, Iterable, cast

from mdforge._norm import CoerceSpec, norm_obj

from ....element import BaseBlockElement, BaseElement
from ....types import AlignType, FlavorType
from ._context import RenderContext
from ._flavors.flavors import lookup_variant
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
        widths: Iterable[int | None] | None = None,
        caption: str | None = None,
        block: bool = False,
        loose: bool = False,
    ):

        def norm_widths(widths: Iterable[int | None]) -> list[int | None]:
            if not isinstance(widths, Iterable):
                raise ValueError(f"Invalid widths, must be iterable: {widths}")

            widths_list: list[Any] = list(widths)
            if not all(
                isinstance(width, (int, NoneType)) for width in widths_list
            ):
                raise ValueError(
                    f"Invalid widths iterable, must contain int or None: {widths}"
                )

            return cast(list[int | None], widths_list)

        self._params = TableParams(
            content_rows=self.__normalize_cells(rows),
            header_rows=self.__normalize_cells(header) if header else None,
            footer_rows=self.__normalize_cells(footer) if footer else None,
            align=align,
            widths=norm_widths(widths) if widths else None,
            caption=caption,
            block=block,
            loose=loose,
        )

        # ensure content is valid given params
        for row in self._params.effective_rows:
            for cell in row:
                if not block and cell._is_block:
                    raise ValueError(
                        f"Inline-only table contains a block element: {cell._element}"
                    )

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:

        # get variant
        variant = lookup_variant(flavor, self._params.block)

        # create context to encapsulate render info
        context = RenderContext(flavor, variant, self._params)

        # render based on variant
        yield from variant.render(context)

    def __normalize_cells(
        self, rows: RowType | Iterable[RowType]
    ) -> list[list[Cell]]:
        """
        Normalize given rows to a list of lists of cells.
        """

        if not (isinstance(rows, Iterable) and len(rows)):
            raise ValueError(f"Invalid row specification: {rows}")

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
            raise ValueError(f"Invalid row or iterable of rows: {rows_list}")

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
