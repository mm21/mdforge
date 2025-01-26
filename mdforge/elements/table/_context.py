"""
Encapsulates context for rendering tables.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Iterable

from ...types import FlavorType
from ._flavors.flavor import BaseTableVariant
from ._params import TableParams
from .cell import VALID_ALIGNS, AlignType


@dataclass(frozen=True)
class RenderContext:

    flavor: FlavorType
    variant: BaseTableVariant
    params: TableParams

    @cached_property
    def col_count(self) -> int:
        """
        Get number of columns.
        """
        return self.params.effective_dims[0]

    @cached_property
    def col_widths(self) -> list[int]:
        """
        Get normalized widths based on params and variant.
        """
        content_widths = self.__get_content_widths()
        assert len(content_widths) == self.col_count

        if self.params.widths:

            # normalize provided widths in case any are None, indicating to
            # use the content width

            assert len(self.params.widths) == self.col_count
            widths: list[int] = []

            for param_width, content_width in zip(
                self.params.widths, content_widths
            ):
                widths.append(param_width or content_width)

            return widths
        else:
            return content_widths

    @cached_property
    def col_aligns(self) -> list[AlignType]:
        """
        Get column alignments.
        """
        match self.params.align:
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
                assert self.params.align is None
                aligns = ["default"] * self.col_count
        return aligns

    def __get_content_widths(self):
        """
        Calculate column widths based on raw (non-wrapped) contents.
        """
        widths: list[int] = [0] * self.col_count

        for row in self.params.effective_rows:
            assert len(row) == self.col_count

            for col_idx, cell in enumerate(row):

                widths[col_idx] = max(
                    widths[col_idx],
                    *(len(line) for line in cell._get_content(self.flavor)),
                )

        return widths
