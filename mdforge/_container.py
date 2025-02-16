"""
Element container functionality.
"""

from __future__ import annotations

from typing import Generator, Iterable, Self

from .element import BaseBlockElement, BaseElement
from .types import FlavorType


class BaseContainer(BaseBlockElement):
    """
    Provides functionality to add and contain block elements.
    """

    _level_inc: int = 1
    """
    Amount by which to increment level of nested containers.
    """

    _level: int | None = None
    """
    Nesting level of this container.
    """

    __elements: list[BaseBlockElement]
    """
    List of nested elements.
    """

    __containers: list[BaseContainer]
    """
    List of nested containers; a subset of `_elements`.
    """

    def __init__(
        self,
        elements: list[BaseElement] | None = None,
        level: int | None = None,
    ):
        self.__elements = []
        self.__containers = []

        if level is not None:
            self.__set_level(level)

        if elements:
            self += elements

    def __iadd__(self, elements: BaseElement | Iterable[BaseElement]) -> Self:
        """
        Implements `+=` operator to add element(s).
        """
        elements_: list[BaseElement] = (
            list(elements) if isinstance(elements, Iterable) else [elements]
        )
        assert all(isinstance(e, BaseElement) for e in elements_)

        # bind elements to this container
        for e in elements_:
            self.__bind_element(e)

        return self

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield "\n\n".join(
            [element._render_block_lines(flavor) for element in self.__elements]
        )

    def __bind_element(self, element: BaseElement):
        """
        Bind element to this container.
        """

        # add to element list
        self.__elements.append(element)

        # set element's container
        element._container = self

        # if element is also a container, bind it
        if isinstance(element, BaseContainer):
            self.__bind_container(element)

    def __bind_container(self, container: BaseContainer):
        """
        Bind another container to this one.
        """
        self.__containers.append(container)

        # propagate level, if set
        if self._level is not None:
            container.__set_level(self._level + self._level_inc)

    def __set_level(self, level: int):
        """
        Set level and propagate recursively.
        """
        assert self._level is None
        self._level = level

        for c in self.__containers:
            c.__set_level(level + self._level_inc)
