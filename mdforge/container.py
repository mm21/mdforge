"""
Element container functionality.
"""

from __future__ import annotations

from typing import Generator, Iterable, Self

from ._norm import CoerceSpec, norm_list
from .element import BaseBlockElement, BaseElement, BaseInlineElement
from .types import FlavorType

__all__ = [
    "InlineContainer",
    "BlockContainer",
]


class InlineContainerMixin:
    """
    Mixin to encapsulate an element which contains one or more inline elements.
    """

    __elements: list[BaseInlineElement]
    __auto_space: bool

    def __init__(
        self, *elements: str | BaseInlineElement, auto_space: bool = False
    ):
        from .elements.inline.text import Text

        self.__elements = norm_list(
            elements, BaseInlineElement, CoerceSpec(Text, str)
        )
        self.__auto_space = auto_space

    def _render_elements(self, flavor: FlavorType) -> str:
        sep = " " if self.__auto_space else ""
        return sep.join(
            element._render_inline(flavor) for element in self.__elements
        )


class InlineContainer(BaseInlineElement, InlineContainerMixin):
    """
    Container for inline elements; wraps multiple inline elements in a single
    one.
    """

    def _render_inline(self, flavor: FlavorType) -> str:
        return self._render_elements(flavor)


class BaseBlockContainer(BaseBlockElement):
    """
    Base class for a block element which contains one or more block elements.
    """

    __elements: list[BaseBlockElement]

    def __init__(self, *elements: BaseElement | str):
        self.__elements = []

        # add elements to this container
        self._add_elements(self._norm_elements(elements))

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield "\n\n".join(
            [element._render_block_lines(flavor) for element in self.__elements]
        )

    def _add_elements(self, elements: list[BaseBlockElement]):
        for element in elements:
            assert isinstance(element, BaseBlockElement)
            self.__elements.append(element)

    def _norm_elements(
        self,
        elements: BaseElement | str | Iterable[BaseElement | str],
    ) -> list[BaseBlockElement]:
        """
        Normalize elements, creating raw block text from strings as necessary.
        """
        from .elements.block.basic import Paragraph, TextBlock

        # - wrap strings in raw text blocks
        # - wrap inline elements in paragraphs
        return norm_list(
            elements,
            BaseBlockElement,
            CoerceSpec(TextBlock, str),
            CoerceSpec(Paragraph, BaseInlineElement),
        )


class BlockContainer(BaseBlockContainer):
    """
    Block element which contains one or more block elements.
    """


class BaseLevelBlockContainer(BaseBlockContainer):
    """
    Base class for a block container which additionally tracks nesting level.
    """

    _level_inc: int = 1
    """
    Amount by which to increment level of nested containers.
    """

    __level: int | None = None
    """
    Nesting level of this container.
    """

    __containers: list[BaseLevelBlockContainer]
    """
    List of nested containers; a subset of nested elements.
    """

    def __init__(self, *elements: BaseElement | str):
        elements_norm = self._norm_elements(elements)

        super().__init__(*elements_norm)
        self.__containers = []

        # bind elements to this container
        self.__bind_elements(elements_norm)

    def __iadd__(
        self,
        elements: BaseElement | str | Iterable[BaseElement | str],
    ) -> Self:
        """
        Implements `+=` operator to add element(s).
        """
        elements_norm = self._norm_elements(elements)

        # add elements to container
        self._add_elements(elements_norm)

        # bind elements to this container
        self.__bind_elements(elements_norm)

        return self

    @property
    def _level(self) -> int:
        assert self.__level is not None
        return self.__level

    @_level.setter
    def _level(self, level: int):
        """
        Set level and propagate recursively.
        """
        assert self.__level is None
        self.__level = level

        for container in self.__containers:
            container._level = level + self._level_inc

    def __bind_elements(self, elements: list[BaseBlockElement]):
        """
        Bind elements to this container.
        """
        for element in elements:

            # set element's container
            element._container = self

            # if element is also a block container, bind it
            if isinstance(element, BaseLevelBlockContainer):
                self.__bind_container(element)

    def __bind_container(self, container: BaseLevelBlockContainer):
        """
        Bind another container to this one.
        """
        self.__containers.append(container)

        # propagate level, if set
        if self.__level is not None:
            container._level = self.__level + self._level_inc
