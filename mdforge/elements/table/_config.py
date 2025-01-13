"""
Table configurations: describe table syntax per Markdown flavor.

In general, a given syntax for a given flavor may or may not support block
content like paragraphs, lists, etc. Therefore each flavor must specify
which configurations to use for inline-only vs block-allowed syntaxes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Separator:
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

    def get_line(self, widths: list[int], config: TableConfig) -> str:
        if not self.line:
            return ""

        inner_corner = (
            self._inner_corner if self._inner_corner is not None else self.line
        )

        if config.cell_sep is None:
            outer_corner = ""
        else:
            outer_corner = (
                self._outer_corner
                if self._outer_corner is not None
                else self.line
            )

        segs: list[str] = []
        for width in widths:

            line_width = width + config.cell_spacing
            segs.append(self.line * line_width)

        return inner_corner.join(segs).join([outer_corner, outer_corner])

    @property
    def _inner_corner(self) -> str | None:
        return self.inner_corner or self.corner

    @property
    def _outer_corner(self) -> str | None:
        return self.outer_corner or self.corner


@dataclass(frozen=True)
class SectionConfig:
    sep: Separator
    upper_sep: Separator | None = None  # defaults to sep
    lower_sep: Separator | None = None  # defaults to sep


@dataclass(frozen=True)
class TableConfig:
    """
    Encapsulates table construction info.
    """

    header: SectionConfig
    content: SectionConfig
    footer: SectionConfig

    cell_sep: str | None = None
    """
    Cell separator, e.g. "|".
    """

    align_char: str | None = None
    """
    Character used to indicate alignment within a separator, e.g. ":" for
    `pandoc`.
    """

    align_space: bool = False
    """
    Whether alignment should be indicated by using spaces in the header.
    """

    @property
    def cell_spacing(self) -> int:
        """
        Number of additional spaces in between each cell.
        """
        return 1 if self.cell_sep is None else 2


@dataclass
class TableFlavor:
    """
    Encapsulates the table configs for a specific flavor.
    """

    inline: TableConfig
    block: TableConfig | None
