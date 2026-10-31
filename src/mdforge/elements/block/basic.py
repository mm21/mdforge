"""
Common block elements.
"""

from __future__ import annotations

from typing import Generator

from ..._norm import CoerceSpec, norm_obj
from ...element import Attributes, BaseBlockElement, BaseInlineElement, RenderContext
from ...exceptions import ValidationError
from ...types import VALID_ALIGNS, AlignType
from .._image import ImageMixin

__all__ = [
    "BlockImage",
]


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

        new_attributes: Attributes | None

        # create new attributes to handle alignment in pandoc
        if align and align != "default":
            attrs: dict[str, str] = {"fig-align": align}
            new_attributes = (
                attributes._copy(attrs=attrs) if attributes else Attributes(attrs=attrs)
            )
        else:
            new_attributes = attributes

        super().__init__(path, attributes=new_attributes)
        self.__caption = norm_obj(
            caption or "", BaseInlineElement, CoerceSpec(Text, str)
        )
        self.__caption._parent = self

    def _render_alt_text(self, context: RenderContext) -> str:
        # note: only pandoc supports inline elements as alt text, which becomes
        # the image caption
        return self.__caption._render_inline(context)

    def _render_block(self, context: RenderContext) -> Generator[str, None, None]:
        yield self._render_commonmark_image(context)
