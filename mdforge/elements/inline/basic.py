"""
Common inline elements.
"""

from __future__ import annotations

from ...element import BaseInlineElement
from ...types import FlavorType
from .._image import ImageMixin

__all__ = [
    "InlineImage",
]


class InlineImage(BaseInlineElement, ImageMixin):
    """
    Inline image.
    """

    def _render_inline(self, flavor: FlavorType) -> str:
        return self._render_image(flavor)
