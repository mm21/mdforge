"""
Element container functionality.
"""

from __future__ import annotations

from typing import Generator, Iterable, Self

from .element import BaseElement
from .types import FlavorType


class BaseContainer(BaseElement):
    """
    Provides functionality to add and contain Markdown elements.
    """

    _elements: list[BaseElement]
    _containers: list[BaseContainer]
    _level: int | None = None
    _level_inc: int = 1

    def __init__(
        self,
        elements: list[BaseElement] | None = None,
        level: int | None = None,
    ):
        self._elements = []
        self._containers = []

        if level is not None:
            self._set_level(level)
        # self._level = level

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
            self._bind_element(e)

        return self

    def _bind_element(self, element: BaseElement):
        """
        Bind element to this container.
        """

        # add to element list
        self._elements.append(element)

        # set element's container
        element._container = self

        # if element is also a container, bind it
        if isinstance(element, BaseContainer):
            self._bind_container(element)

    def _bind_container(self, container: BaseContainer):
        """
        Bind another container to this one.
        """
        self._containers.append(container)

        # propagate level, if set
        if self._level is not None:
            container._set_level(self._level + self._level_inc)

    def _set_level(self, level: int):
        """
        Set level and propagate recursively.
        """
        assert self._level is None
        self._level = level

        for c in self._containers:
            c._set_level(level + self._level_inc)

    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        """ """
        blocks: list[str] = []

        for element in self._elements:
            blocks.append("\n".join(element._render_element(flavor)))

        yield "\n\n".join(blocks)
