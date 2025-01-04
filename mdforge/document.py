"""
Interface for Markdown document generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ._container import BaseContainer
from .types import FlavorType

__all__ = [
    "Document",
]

ROOT_LEVEL: int = 1


class Document(BaseContainer):
    """
    Encapsulates a Markdown document. Add elements using the `+=` operator.
    """

    _level_inc: int = 0
    """
    Treat all nested containers as top-level sections.
    """

    _frontmatter: dict[str, Any] | None

    def __init__(self, frontmatter: dict[str, Any] | None = None):
        super().__init__(level=ROOT_LEVEL)
        self._frontmatter = frontmatter

    def render(self, path: Path, flavor: FlavorType = "commonmark"):
        """
        Write Markdown document to the provided path using the provided flavor.
        """
        with path.open("w") as fh:
            fh.write(self.render_text(flavor=flavor))

    def render_text(self, flavor: FlavorType = "commonmark") -> str:
        """
        Return Markdown document as text.
        """
        frontmatter = self._render_frontmatter()
        content: str = "\n\n".join(list(self._render_element(flavor)))
        return f"{frontmatter or ''}{content}\n"

    def _render_frontmatter(self) -> str | None:
        if self._frontmatter is None:
            return None

        content = yaml.dump(
            self._frontmatter, default_flow_style=False, sort_keys=False
        )
        return f"---\n{content}---\n"
