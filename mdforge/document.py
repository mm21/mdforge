"""
Interface for Markdown document generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

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

    def render(self, *, flavor: FlavorType) -> str:
        """
        Return Markdown document using the provided flavor as a string.
        """
        frontmatter = self.__render_frontmatter()
        content: str = "\n\n".join(self._render_block(flavor))
        return f"{frontmatter or ''}{content}\n"

    def render_file(self, path: Path | str, *, flavor: FlavorType):
        """
        Write Markdown document using the provided flavor to the provided file.
        """
        path_norm = path if isinstance(path, Path) else Path(path)
        with path_norm.open("w") as fh:
            fh.write(self.render(flavor=flavor))

    def get_pandoc_extensions(self) -> list[str]:
        """
        Get a list of extensions required to convert the resulting
        markdown document in pandoc, assuming pandoc flavor is used for
        rendering.
        """
        return sorted(self._get_pandoc_extensions())

    def __render_frontmatter(self) -> str | None:
        if self.__frontmatter is None:
            return None

        content = yaml.dump(
            self.__frontmatter, default_flow_style=False, sort_keys=False
        )
        return f"---\n{content}---\n"
