"""
Section element to encapsulate user-defined sections with optional
heading management.
"""

from __future__ import annotations

from ..._norm import CoerceSpec, norm_obj
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

    __heading: Heading | None

    def __init__(
        self,
        *elements: BaseBlockElement | str,
        heading: str | Heading | None = None,
    ):
        # create heading if given, inserting as first element
        heading_norm = (
            norm_obj(heading, Heading, CoerceSpec(Heading, str))
            if heading
            else None
        )
        self.__heading = heading_norm

        super().__init__(*([heading_norm] if heading_norm else []), *elements)

    @property
    def _heading(self) -> Heading | None:
        return self.__heading
