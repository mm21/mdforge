"""
Common inline elements.
"""

from ...container import InlineContainerMixin
from ...element import BaseInlineElement
from ...types import FlavorType

__all__ = [
    "Text",
    "Emph",
    "Strong",
    "Underline",
    "Strikethrough",
]


class BaseTextContainer(BaseInlineElement, InlineContainerMixin):
    """
    Inline element containing text or a list of inline elements.
    """

    def _render_inline(self, flavor: FlavorType) -> str:
        return self._render_elements(flavor)


class Text(BaseInlineElement):
    """
    Inline element containing a single string.
    """

    __text: str

    def __init__(self, text: str):
        self.__text = text

    def _render_inline(self, _: FlavorType) -> str:
        return self.__text


class Emph(BaseTextContainer):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"_{super()._render_inline(flavor)}_"


class Strong(BaseTextContainer):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"**{super()._render_inline(flavor)}**"


class Underline(BaseTextContainer):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"<u>{super()._render_inline(flavor)}</u>"


class Strikethrough(BaseTextContainer):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"~~{super()._render_inline(flavor)}~~"


# TODO: span
