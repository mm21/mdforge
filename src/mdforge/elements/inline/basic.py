"""
Common inline elements.
"""

from __future__ import annotations

from ...element import Attributes, AttributesMixin, BaseInlineElement
from ...types import FlavorType
from .._image import ImageMixin
from .text import BaseTextContainer

__all__ = [
    "Span",
    "InlineImage",
]


class Span(AttributesMixin, BaseTextContainer):
    """
    Span element; a container for inline elements which can have its own
    attributes.
    """

    def __init__(
        self,
        *elements: BaseInlineElement | str,
        auto_space: bool = False,
        attributes: Attributes | None = None,
    ):
        super().__init__(*elements, auto_space=auto_space)
        self._set_attrs(attributes)

    def _render_inline(self, flavor: FlavorType) -> str:
        text = super()._render_inline(flavor)
        attrs = self._get_attrs_str(flavor)
        return f"[{text}]{attrs}"

    def _get_pandoc_extensions(self) -> set[str]:
        return (
            {"bracketed_spans"} if self._has_attrs else set()
        ) | super()._get_pandoc_extensions()


class InlineImage(BaseInlineElement, ImageMixin):
    """
    Inline image.
    """

    __alt_text: str

    def __init__(
        self,
        path: str,
        alt_text: str | None = None,
        *,
        attributes: Attributes | None = None,
    ):
        super().__init__(path, attributes=attributes)
        self.__alt_text = alt_text or ""

    def _render_alt_text(self, _: FlavorType) -> str:
        # note: no markdown flavors support inline elements as alt text
        return self.__alt_text

    def _render_inline(self, flavor: FlavorType) -> str:
        return self._render_commonmark_image(flavor)
