"""
Table element.
"""

from __future__ import annotations

from typing import Generator, cast

from ....element import BaseBlockElement, BaseElement
from ....types import FlavorType
from ._context import RenderContext
from ._flavors.flavors import lookup_variant
from ._params import TableParams
from .cell import AlignType, Cell, RowType

__all__ = [
    "Table",
]


class Table(BaseBlockElement):

    _params: TableParams
    """
    Immutable table parameters as passed by user.
    """

    def __init__(
        self,
        rows: list[RowType],
        header: RowType | list[RowType] | None = None,
        footer: RowType | list[RowType] | None = None,
        align: AlignType | list[AlignType] | None = None,
        widths: list[int | None] | None = None,
        caption: str | None = None,
        block: bool = False,
    ):
        self._params = TableParams(
            content_rows=self.__normalize_cells(rows),
            header_rows=self.__normalize_cells(header) if header else None,
            footer_rows=self.__normalize_cells(footer) if footer else None,
            align=align,
            widths=widths,
            caption=caption,
            block=block,
        )

        # ensure content is valid given params
        for row in self._params.effective_rows:
            for cell in row:
                if isinstance(cell.content, BaseElement):
                    if not block and isinstance(cell.content, BaseBlockElement):
                        raise ValueError(
                            f"Inline-only table contains a block element: {cell.content}"
                        )

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:

        # get variant
        variant = lookup_variant(flavor, self._params.block)

        # create context to encapsulate render info
        context = RenderContext(flavor, variant, self._params)

        # render based on variant
        yield from variant.render(context)

    def __normalize_cells(
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
