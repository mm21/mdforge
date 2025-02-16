"""
Base element functionality.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator

from .types import FlavorType

if TYPE_CHECKING:
    from ._container import BaseContainer

__all__ = [
    "BaseElement",
    "BaseInlineElement",
    "BaseBlockElement",
]


class BaseElement(ABC):

    __container: BaseContainer | None = None

    @property
    def _container(self) -> BaseContainer:
        assert (
            self.__container
        ), f"Element has not been placed in a container: {self}"
        return self.__container

    @_container.setter
    def _container(self, container: BaseContainer):
        assert self.__container is None
        self.__container = container


class BaseInlineElement(BaseElement):
    """
    Base inline element, rendering a single string.
    """

    @abstractmethod
    def _render_inline(self, flavor: FlavorType) -> str:
        """
        Render by returning a single string.
        """
        ...


class BaseBlockElement(BaseElement):
    """
    Base block element, rendering multiple strings.
    """

    @abstractmethod
    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        """
        Render by yielding each line.
        """
        ...

    def _render_block_lines(self, flavor: FlavorType) -> str:
        """
        Render as multi-line string.
        """
        return "\n".join(self._render_block(flavor))
