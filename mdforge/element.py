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
]


class BaseElement(ABC):

    __container: BaseContainer | None = None

    @abstractmethod
    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        """
        Render by yielding each line.
        """
        ...

    def _render_str(self, flavor: FlavorType):
        """
        Render as multi-line string.
        """
        return "\n".join(self._render_element(flavor))

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
