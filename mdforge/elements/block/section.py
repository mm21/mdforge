"""
Section element to encapsulate user-defined sections with optional
heading management.
"""

from __future__ import annotations

from ..._containers import BaseBlockElementContainer
from ...element import BaseElement
from .common import Heading

__all__ = [
    "Section",
]


class Section(BaseBlockElementContainer):

    __heading: Heading | None

    def __init__(
        self,
        heading: str | None = None,
        elements: list[BaseElement] | None = None,
    ):
        self.__heading = Heading(heading) if heading else None
        elements = ([self.__heading] if self.__heading else []) + (
            elements or []
        )
        super().__init__(elements=elements)

    @property
    def heading(self) -> Heading:
        """
        Get heading, ensuring it was set when this section was created.
        """
        if self.__heading is None:
            raise ValueError("Heading not set when section was created")
        return self.__heading
