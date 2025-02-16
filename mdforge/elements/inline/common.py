"""
Common inline elements.
"""

from ...element import BaseInlineElement
from ...types import FlavorType

__all__ = [
    "Text",
    "Emph",
    "Strong",
    "Underline",
    "Strikethrough",
]


class BaseInlineContainerElement(BaseInlineElement):
    """
    Inline element containing text or a list of inline elements.
    """

    __elements: list[BaseInlineElement]
    __auto_space: bool

    def __init__(
        self, *elements: str | BaseInlineElement, auto_space: bool = True
    ):
        self.__elements = self.__normalize_elements(list(elements))
        self.__auto_space = auto_space

    def _render_inline(self, flavor: FlavorType) -> str:
        sep = " " if self.__auto_space else ""
        return sep.join(
            element._render_inline(flavor) for element in self.__elements
        )

    def __normalize_elements(
        self, raw_elements: list[str | BaseInlineElement]
    ) -> list[BaseInlineElement]:
        """
        Normalize inline elements, creating text elements from strings as
        necessary.
        """
        elements: list[BaseInlineElement] = []

        for element in raw_elements:
            if isinstance(element, BaseInlineElement):
                elements.append(element)
            else:
                if not isinstance(element, str):
                    raise ValueError(
                        f"Invalid element, must be str or inline element: {element}"
                    )
                elements.append(Text(element))

        return elements


class Text(BaseInlineElement):
    """
    Inline element containing a single string.
    """

    __text: str

    def __init__(self, text: str):
        self.__text = text

    def _render_inline(self, _: FlavorType) -> str:
        return self.__text


class Emph(BaseInlineContainerElement):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"_{super()._render_inline(flavor)}_"


class Strong(BaseInlineElement):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"**{super()._render_inline(flavor)}**"


class Underline(BaseInlineElement):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"<u>{super()._render_inline(flavor)}</u>"


class Strikethrough(BaseInlineElement):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"~~{super()._render_inline(flavor)}~~"
