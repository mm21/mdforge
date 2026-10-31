"""
Element container functionality.
"""

from __future__ import annotations

from typing import Generator, Iterable, Self

from ._norm import CoerceSpec, norm_list
from ._utils import check_level, coerce_inline_text, validate_level
from .element import (
    BaseBlockElement,
    BaseElement,
    BaseInlineElement,
    BaseNode,
    RenderContext,
)
from .exceptions import ValidationError

__all__ = [
    "InlineContainer",
    "BlockContainer",
]

ROOT_LEVEL: int = 1
"""
Nesting level of the element being rendered, e.g. a document or a standalone section,
unless it has an explicit level.
"""


class InlineContainerMixin(BaseElement):
    """
    Mixin to encapsulate an element which contains one or more inline elements.
    """

    _allow_multiline: bool = False
    """
    Whether to allow text elements containing newlines, but no blank lines.
    """

    __elements: list[BaseInlineElement]
    __auto_space: bool

    def __init__(self, *elements: BaseInlineElement | str, auto_space: bool = False):
        def coerce(obj: str) -> BaseInlineElement:
            return coerce_inline_text(obj, allow_multiline=self._allow_multiline)

        self.__elements = norm_list(
            elements, BaseInlineElement, CoerceSpec(coerce, str)
        )
        self.__auto_space = auto_space

        for element in self.__elements:
            element._parent = self

        self._inline_post_init()

    def _inline_post_init(self):
        """
        Optionally overridden by subclass to perform additional init.
        """

    def _render_elements(self, context: RenderContext) -> str:
        sep = " " if self.__auto_space else ""
        return sep.join(element._render_inline(context) for element in self.__elements)

    def _get_pandoc_extensions(self) -> set[str]:
        return _aggregate_extensions(self.__elements) | super()._get_pandoc_extensions()


class InlineContainer(InlineContainerMixin, BaseInlineElement):
    """
    Container for inline elements; wraps multiple inline elements in a single one.
    """

    def _render_inline(self, context: RenderContext) -> str:
        return self._render_elements(context)


class BaseBlockContainer(BaseBlockElement):
    """
    Base class for a block element which contains one or more block elements.
    """

    __elements: list[BaseBlockElement]

    def __init__(self):
        self.__elements = []

    def __iadd__(
        self,
        elements: BaseElement | str | Iterable[BaseElement | str],
    ) -> Self:
        """
        Implement `+=` operator to add element(s).
        """
        self._add_elements(self._norm_elements(elements))
        return self

    def _get_descendants(self) -> Generator[BaseBlockElement, None, None]:
        """
        Get all nested block elements, recursing into nested block containers.
        """
        for element in self.__elements:
            yield element
            if isinstance(element, BaseBlockContainer):
                yield from element._get_descendants()

    def _get_child_level(self, context: RenderContext) -> int:
        """
        Get nesting level of level containers nested in this one.
        """
        if self is context.root:
            return ROOT_LEVEL
        return self._container._get_child_level(context)

    def _validate_parent(self, parent: BaseNode):
        """
        Ensure this container neither is nor contains a section if placed in content
        which can't contain sections.
        """
        location = parent._get_content_location()
        if location is None:
            return

        elements = [self, *self._get_descendants()]
        if any(isinstance(elem, BaseLevelBlockContainer) for elem in elements):
            raise ValidationError(f"Sections cannot be placed in {location}: {self}")

    def _render_block(self, context: RenderContext) -> Generator[str, None, None]:
        yield "\n\n".join(
            ["\n".join(element._render_block(context)) for element in self.__elements]
        )

    def _get_pandoc_extensions(self) -> set[str]:
        return _aggregate_extensions(self.__elements) | super()._get_pandoc_extensions()

    def _add_elements(self, elements: list[BaseBlockElement]):
        """
        Add elements to container and set this as their parent.
        """
        for element in elements:
            assert isinstance(element, BaseBlockElement)
            element._parent = self
            self.__elements.append(element)

    def _norm_elements(
        self,
        elements: BaseElement | str | Iterable[BaseElement | str],
    ) -> list[BaseBlockElement]:
        """
        Normalize elements, creating raw block text from strings as necessary.
        """
        from .elements.block.text import BlockText, Paragraph

        # - wrap strings in raw text blocks
        # - wrap inline elements in paragraphs
        return norm_list(
            elements,
            BaseBlockElement,
            CoerceSpec(BlockText, str),
            CoerceSpec(Paragraph, BaseInlineElement),
        )


class BlockContainer(BaseBlockContainer):
    """
    Block element which contains one or more block elements.
    """

    def __init__(self, *elements: BaseElement | str):
        super().__init__()
        self += elements


class BaseLevelBlockContainer(BaseBlockContainer):
    """
    Base class for a block container which additionally tracks nesting level.
    """

    _level_inc: int = 1
    """
    Amount by which to increment level of nested containers.
    """

    __level: int | None
    """
    Explicit level, invariant of placement, or `None` to infer from placement relative
    to the render root.
    """

    def __init__(self, level: int | None = None):
        super().__init__()
        validate_level(level)
        self.__level = level

    def _get_level(self, context: RenderContext) -> int:
        if self.__level is not None:
            return self.__level
        if self is context.root:
            return ROOT_LEVEL
        return self._container._get_child_level(context)

    def _get_child_level(self, context: RenderContext) -> int:
        return self._get_level(context) + self._level_inc

    def _render_block(self, context: RenderContext) -> Generator[str, None, None]:
        if self.__level is not None and self is not context.root:
            check_level(
                self._get_desc(context),
                self.__level,
                self._container._get_child_level(context),
            )
        yield from super()._render_block(context)

    def _get_desc(self, context: RenderContext) -> str:
        """
        Get description of this container for error messages.
        """
        return str(self)


def _aggregate_extensions(elements: Iterable[BaseElement]) -> set[str]:
    """
    Aggregate extensions from elements.
    """
    extensions: set[str] = set()
    for elem in elements:
        extensions |= elem._get_pandoc_extensions()
    return extensions
