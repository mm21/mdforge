"""
Common block elements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from ...container import InlineContainerMixin
from ...element import Attributes, AttributesMixin, BaseBlockElement
from ...types import VALID_ALIGNS, AlignType, FlavorType
from .._image import ImageMixin

__all__ = [
    "Heading",
    "Paragraph",
    "BlockText",
    "BlockImage",
]


@dataclass
class Heading(BaseBlockElement, AttributesMixin):
    """
    Heading, e.g. `# My heading`. If `level` not provided, it is set
    automatically based on nesting of container.
    """

    __text: str
    """
    Heading text.
    """

    __level: int | None
    """
    Heading level, or `None` to set automatically.
    """

    def __init__(
        self,
        text: str,
        level: int | None = None,
        *,
        attributes: Attributes | None = None,
    ):
        self.__text = text
        self.__level = level
        self._set_attrs(attributes)

    @property
    def _text(self) -> str:
        return self.__text

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        level = self.__level or self._container._level
        yield f"{'#' * level} {self.__text}{self._get_attrs_str(flavor, space_prefix=True)}"


class Paragraph(BaseBlockElement, InlineContainerMixin):

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield self._render_elements(flavor)


class BlockText(BaseBlockElement):
    """
    Block element containing a single string, which may have multiple lines.
    """

    __lines: list[str]

    def __init__(self, text: str):
        self.__lines = text.strip().split("\n")

    @property
    def _has_empty_lines(self) -> bool:
        """
        Check if text block has any empty lines.
        """
        return any(line.strip() == "" for line in self.__lines)

    def _render_block(self, _: FlavorType) -> Generator[str, None, None]:
        yield from self.__lines


class BlockImage(BaseBlockElement, ImageMixin):
    """
    Block image.
    """

    def __init__(
        self,
        path: str,
        alt_text: str | None = None,
        *,
        attributes: Attributes | None = None,
        align: AlignType | None = None,
    ):
        if align and align not in VALID_ALIGNS:
            raise ValueError(f"Invalid alignment: {align}")

        # create new attributes to handle alignment in pandoc
        if align and align != "default":
            attrs = {"fig-align": align}
            new_attributes = (
                attributes._copy(attrs=attrs)
                if attributes
                else Attributes(attrs=attrs)
            )
        else:
            new_attributes = attributes

        super().__init__(path, alt_text=alt_text, attributes=new_attributes)

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield self._render_image(flavor)
