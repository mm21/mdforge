"""
Implements image handling.
"""

from __future__ import annotations

from ..element import Attributes, AttributesMixin
from ..types import FlavorType

__all__ = [
    "ImageMixin",
]


class ImageMixin(AttributesMixin):
    """
    Mixin to implement common image handling between inline and block images.
    """

    __path: str
    __alt_text: str

    def __init__(
        self,
        path: str,
        alt_text: str | None = None,
        *,
        attributes: Attributes | None = None,
    ):
        self.__path = path
        self.__alt_text = alt_text or ""
        self._set_attrs(attributes)

    def _render_image(self, flavor: FlavorType) -> str:
        attrs = self._get_attrs_str(flavor)
        return f"![{self.__alt_text}]({self.__path}){attrs}"
