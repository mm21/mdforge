"""
Section "pseudo-element" to encapsulate user-defined sections with optional
heading management.
"""

from __future__ import annotations

from .._container import BaseContainer
from ..element import BaseElement
from .basic import Heading

__all__ = [
    "Section",
]


class Section(BaseContainer):

    def __init__(
        self,
        heading: str | None = None,
        elements: list[BaseElement] | None = None,
    ):
        elements = ([Heading(heading)] if heading else []) + (elements or [])
        super().__init__(elements=elements)
