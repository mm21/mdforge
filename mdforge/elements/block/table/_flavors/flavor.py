"""
Table configurations: describe table syntax per Markdown flavor.

In general, a given syntax for a given flavor may or may not support block
content like paragraphs, lists, etc. Therefore each flavor must specify
which configurations to use for inline-only vs block-allowed syntaxes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator

from .._params import TableParams

if TYPE_CHECKING:
    from .._context import RenderContext

__all__ = [
    "TableFlavor",
    "BaseTableVariant",
]


@dataclass(frozen=True)
class TableFlavor:
    """
    Encapsulates table configs for a specific Markdown flavor,
    distinguishing between tables supporting block elements vs inline-only.
    """

    inline: BaseTableVariant
    block: BaseTableVariant | None


@dataclass(frozen=True, kw_only=True)
class BaseTableVariant(ABC):
    """
    Base class to encapsulate a table variant.
    """

    cell_sep: str
    """
    Separator between cells.
    """

    row_leading_sep: str
    """
    Separator at beginning of row.
    """

    row_trailing_sep: str
    """
    Separator at end of row.
    """

    wrap: bool = True
    """
    Whether to wrap words when cell contents exceed fixed column
    width.
    """

    align_space: bool = False
    """
    Whether alignment should be indicated by using spaces in the header.
    """

    align_char: str | None = None
    """
    Character used to indicate alignment within a separator, e.g. ":" for
    `pandoc`.
    """

    @abstractmethod
    def validate_params(self, params: TableParams):
        """
        Ensure this variant can be rendered given params.
        """
        ...

    @abstractmethod
    def render(self, context: RenderContext) -> Generator[str, None, None]:
        """
        Render this table using the provided context.
        """
        ...
