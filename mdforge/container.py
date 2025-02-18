"""
Element container functionality.
"""

from __future__ import annotations

from typing import Generator, Iterable, Self

from .element import BaseBlockElement, BaseInlineElement
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
        self.__elements = self.__normalize_elements(list(elements))
        self.__auto_space = auto_space

    def _render_elements(self, flavor: FlavorType) -> str:
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

        from .elements.inline.text import Text

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

    def __init__(self, *elements: BaseBlockElement):
        self.__elements = []

        for element in elements:
            self._add_element(element)

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield "\n\n".join(
            [element._render_block_lines(flavor) for element in self.__elements]
        )

    def _add_element(self, element: BaseBlockElement):
        if not isinstance(element, BaseBlockElement):
            raise ValueError

        self.__elements.append(element)


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

    def __init__(
        self,
        *elements: BaseBlockElement,
    ):
        super().__init__(*elements)
        self.__containers = []

        # bind elements
        for element in elements:
            self.__bind_element(element)

    def __iadd__(
        self, elements: BaseBlockElement | Iterable[BaseBlockElement]
    ) -> Self:
        """
        Implements `+=` operator to add element(s).
        """
        elements_: list[BaseBlockElement] = (
            list(elements) if isinstance(elements, Iterable) else [elements]
        )

        # add and bind elements to this container
        for element in elements_:
            # add to element list
            self._add_element(element)
            self.__bind_element(element)

        return self

    @property
    def _level(self) -> int | None:
        return self.__level

    @_level.setter
    def _level(self, level: int):
        """
        Set level and propagate recursively.
        """
        assert self.__level is None
        self.__level = level

        for c in self.__containers:
            c._level = level + self._level_inc

    def __bind_element(self, element: BaseBlockElement):
        """
        Bind element to this container.
        """

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
