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


class Span(BaseTextContainer, AttributesMixin):
    """
    Span element; a container for inline elements which can have its own
    attributes.
    """

    def __init__(
        self,
        *elements: str | BaseInlineElement,
        auto_space: bool = False,
        attributes: Attributes | None = None,
    ):
        super().__init__(*elements, auto_space=auto_space)
        self._set_attrs(attributes)

    def _render_inline(self, flavor: FlavorType) -> str:
        text = super()._render_inline(flavor)
        attrs = self._get_attrs_str(flavor)
        return f"[{text}]{attrs}"


class InlineImage(BaseInlineElement, ImageMixin):
    """
    Inline image.
    """

    def _render_inline(self, flavor: FlavorType) -> str:
        return self._render_image(flavor)
