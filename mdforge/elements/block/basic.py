"""
Common block elements.
"""

from __future__ import annotations

from typing import Generator

from ..._norm import CoerceSpec, norm_obj
from ...element import (
    Attributes,
    AttributesMixin,
    BaseBlockElement,
    BaseInlineElement,
)
from ...exceptions import ValidationError
from ...types import VALID_ALIGNS, AlignType, FlavorType
from .._image import ImageMixin

__all__ = [
    "Heading",
    "BlockImage",
]


class Heading(AttributesMixin, BaseBlockElement):
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

    def _get_pandoc_extensions(self) -> set[str]:
        return (
            {"header_attributes"} if self._has_attrs else set()
        ) | super()._get_pandoc_extensions()


class BlockImage(BaseBlockElement, ImageMixin):
    """
    Block image.
    """

    __caption: BaseInlineElement

    def __init__(
        self,
        path: str,
        caption: BaseInlineElement | str | None = None,
        align: AlignType | None = None,
        *,
        attributes: Attributes | None = None,
    ):
        from ..inline.text import Text

        if align and align not in VALID_ALIGNS:
            raise ValidationError(f"Invalid alignment: {align}")

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

        super().__init__(path, attributes=new_attributes)
        self.__caption = norm_obj(
            caption or "", BaseInlineElement, CoerceSpec(Text, str)
        )

    def _render_alt_text(self, flavor: FlavorType) -> str:
        # note: only pandoc supports inline elements as alt text, which becomes
        # the image caption
        return self.__caption._render_inline(flavor)

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield self._render_commonmark_image(flavor)
