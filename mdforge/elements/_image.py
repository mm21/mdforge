"""
Implements image handling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..element import Attributes, AttributesMixin
from ..types import FlavorType

__all__ = [
    "ImageMixin",
]


class ImageMixin(AttributesMixin, ABC):
    """
    Mixin to implement common image handling between inline and block images.
    """

    __path: str

    def __init__(
        self,
        path: str,
        *,
        attributes: Attributes | None = None,
    ):
        self.__path = path
        self._set_attrs(attributes)

    @abstractmethod
    def _render_alt_text(self, _: FlavorType) -> str:
        """
        Implemented by concrete class to get alt text.
        """
        ...

    def _render_commonmark_image(self, flavor: FlavorType) -> str:
        """
        Render image with CommonMark syntax.
        """
        attrs = self._get_attrs_str(flavor)
        return f"![{self._render_alt_text(flavor)}]({self.__path}){attrs}"
