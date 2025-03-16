from __future__ import annotations

from dataclasses import dataclass

from ......exceptions import RenderError
from ..._params import TableParams
from ..._variant import BaseTableVariant

__all__ = [
    "SeparatorConfig",
    "SectionConfig",
    "FrameTableVariant",
]


@dataclass(frozen=True)
class SeparatorConfig:
    """
    Encapsulates a table separator.
    """

    line: str | None = "-"
    """
    Base character for the line, i.e. "-" or "=".
    """

    inner_corner: str | None = None
    """
    Innermost corner character.
    """

    outer_corner: str | None = None
    """
    Outermost corner character.
    """

    corner: str | None = None
    """
    Corner character for both inner and outer corners.
    """

    @property
    def inner_corner_norm(self) -> str:
        return (
            self.inner_corner
            if self.inner_corner is not None
            else self.__default_corner
        )

    @property
    def outer_corner_norm(self) -> str:
        return (
            self.outer_corner
            if self.outer_corner is not None
            else self.__default_corner
        )

    @property
    def __default_corner(self) -> str:
        return (self.corner if self.corner is not None else self.line) or ""


@dataclass(frozen=True)
class SectionConfig:
    """
    Encapsulates section info, i.e. header/content/footer.
    """

    middle_sep: SeparatorConfig
    upper_sep: SeparatorConfig | None = None
    lower_sep: SeparatorConfig | None = None

    @property
    def upper_sep_norm(self) -> SeparatorConfig:
        return self.upper_sep or self.middle_sep

    @property
    def lower_sep_norm(self) -> SeparatorConfig:
        return self.lower_sep or self.middle_sep


@dataclass(frozen=True, kw_only=True)
class FrameTableVariant(BaseTableVariant):
    """
    Encapsulates frame table construction info.
    """

    header_section: SectionConfig
    """
    Configuration for table header.
    """

    content_section: SectionConfig
    """
    Configuration for table content.
    """

    footer_section: SectionConfig | None = None
    """
    Configuration for table footer.
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

    def validate_params(self, params: TableParams):

        if params.footer_rows and not self.footer_section:
            raise RenderError(
                f"Table variant '{self.name}' does not support footer rows, try passing block=True"
            )
