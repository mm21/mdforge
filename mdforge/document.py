"""
Interface for Markdown document generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ._containers import BaseBlockElementContainer
from .element import BaseElement
from .types import FlavorType

__all__ = [
    "Document",
]

ROOT_LEVEL: int = 1


class Document(BaseBlockElementContainer):
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
        frontmatter: dict[str, Any] | None = None,
        elements: list[BaseElement] | None = None,
    ):
        super().__init__(elements=elements, level=ROOT_LEVEL)
        self.__frontmatter = frontmatter

    def render(self, path: Path, *, flavor: FlavorType):
        """
        Write Markdown document to the provided path using the provided flavor.
        """
        with path.open("w") as fh:
            fh.write(self.render_text(flavor=flavor))

    def render_text(self, *, flavor: FlavorType) -> str:
        """
        Return Markdown document as text.
        """
        frontmatter = self.__render_frontmatter()
        content: str = "\n\n".join(list(self._render_block(flavor)))
        return f"{frontmatter or ''}{content}\n"

    def __render_frontmatter(self) -> str | None:
        if self.__frontmatter is None:
            return None

        content = yaml.dump(
            self.__frontmatter, default_flow_style=False, sort_keys=False
        )
        return f"---\n{content}---\n"
