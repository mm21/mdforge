"""
Interface for Markdown document generation.
"""

from pathlib import Path
from typing import Any, Iterable, Self

from ._element import BaseElement


class Document:
    """
    Encapsulates a Document. Add element(s) using the `+=` operator.
    """

    _frontmatter: dict[str, Any] | None
    _elements: list[BaseElement]

    def __init__(self, frontmatter: dict[str, Any] | None = None):
        self._frontmatter = frontmatter
        self._elements = []

    def __iadd__(self, element: BaseElement | Iterable[BaseElement]) -> Self:
        """
        Implements `+=` operator to add element(s).
        """
        elements: list[BaseElement] = (
            list(element) if isinstance(element, Iterable) else [element]
        )
        assert all(isinstance(e, BaseElement) for e in elements)

        self._elements += elements

        return self

    def render(self, path: Path):
        """
        Write Markdown document to the provided path.
        """
        with path.open("w") as fh:
            fh.write(self.render_text())

    def render_text(self) -> str:
        """
        Return Markdown document as text.
        """

        lines: list[str] = []

        if self._frontmatter is not None:
            # TODO: write frontmatter
            pass

        for element in self._elements:
            lines += list(element.render()) + [""]

        return "\n".join(lines)
