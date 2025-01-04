"""
Section "pseudo-element" to encapsulate user-defined sections with optional
heading management.
"""

from __future__ import annotations

from .._container import BaseContainer
from .basic import Heading

__all__ = [
    "Section",
]


class Section(BaseContainer):

    def __init__(self, heading: str | None = None):
        if heading:
            # add heading as first element of this section
            self += Heading(heading)
