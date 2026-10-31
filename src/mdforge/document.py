"""
Interface for Markdown document generation.
"""

from __future__ import annotations

from typing import Any, Generator, Iterable, Mapping

import yaml

from .container import BaseLevelBlockContainer
from .element import BaseElement, RenderContext

__all__ = [
    "Document",
]

ROOT_LEVEL: int = 1


class Document(BaseLevelBlockContainer):
    """
    Encapsulates a Markdown document.

    Add elements using the `+=` operator.
    """

    _level_inc: int = 0
    """
    Treat all nested containers as top-level sections.
    """

    __frontmatter: Mapping[str, Any] | None

    def __init__(
        self,
        *,
        frontmatter: Mapping[str, Any] | None = None,
        elements: BaseElement | str | Iterable[BaseElement | str] | None = None,
    ):
        super().__init__()
        self.__frontmatter = frontmatter

        if elements:
            self += elements

    def _get_level(self) -> int:
        return ROOT_LEVEL

    def _render_block(self, context: RenderContext) -> Generator[str, None, None]:
        yield from self.__render_frontmatter()
        yield from super()._render_block(context)
        yield ""

    def __render_frontmatter(self) -> Generator[str, None, None]:
        if self.__frontmatter is None:
            return None

        content = yaml.dump(
            dict(self.__frontmatter), default_flow_style=False, sort_keys=False
        )
        yield from ["---", f"{content}---", ""]
