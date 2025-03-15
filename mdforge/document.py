"""
Interface for Markdown document generation.
"""

from __future__ import annotations

from typing import Any, Generator, Iterable

import yaml

from .container import BaseLevelBlockContainer
from .element import BaseElement
from .types import FlavorType

__all__ = [
    "Document",
]

ROOT_LEVEL: int = 1


class Document(BaseLevelBlockContainer):
    """
    Encapsulates a Markdown document. Add elements using the `+=` operator.
    """

    _level_inc: int = 0
    """
    Treat all nested containers as top-level sections.
    """

    __frontmatter: dict[str, Any] | None

    def __init__(
        self,
        *,
        frontmatter: dict[str, Any] | None = None,
        elements: BaseElement | str | Iterable[BaseElement | str] | None = None,
    ):
        super().__init__()
        self.__frontmatter = frontmatter
        self._level = ROOT_LEVEL

        if elements:
            self += elements

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield from self.__render_frontmatter()
        yield from super()._render_block(flavor)
        yield ""

    def __render_frontmatter(self) -> Generator[str, None, None]:
        if self.__frontmatter is None:
            return None

        content = yaml.dump(
            self.__frontmatter, default_flow_style=False, sort_keys=False
        )
        yield from ["---", f"{content}---", ""]
