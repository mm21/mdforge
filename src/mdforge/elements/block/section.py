"""
Section element to encapsulate user-defined sections with optional
heading management.
"""

from __future__ import annotations

from typing import Iterable

from ..._norm import CoerceSpec, norm_obj
from ...container import BaseLevelBlockContainer
from ...element import BaseElement
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

    __heading: Heading | None = None

    def __init__(
        self,
        heading: Heading | str | None = None,
        *,
        elements: BaseElement | str | Iterable[BaseElement | str] | None = None,
    ):
        super().__init__()

        # create heading if given and add as first element
        if heading:
            self.__heading = norm_obj(
                heading, Heading, CoerceSpec(Heading, str)
            )
            self += self.__heading

        if elements:
            self += elements

    @property
    def _heading(self) -> Heading | None:
        return self.__heading
