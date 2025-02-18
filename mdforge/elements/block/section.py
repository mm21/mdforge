"""
Section element to encapsulate user-defined sections with optional
heading management.
"""

from __future__ import annotations

from ...container import BaseLevelBlockContainer
from ...element import BaseBlockElement
from .basic import Heading

__all__ = [
    "Section",
]


class Section(BaseLevelBlockContainer):
    """
    Encapsulates a logical document section, containing block elements with
    an optional heading. Heading level is inferred by this section's nesting
    level.
    """

    def __init__(
        self,
        *elements: BaseBlockElement,
        heading: str | None = None,
    ):
        # create heading if given, inserting as first element
        heading_ = tuple([Heading(heading)]) if heading else None
        super().__init__(*heading_, *elements)
