"""
Element container functionality.
"""

from __future__ import annotations

from typing import Generator, Iterable, Self

from ._norm import CoerceSpec, norm_list
from ._utils import coerce_inline_text
from .element import BaseBlockElement, BaseElement, BaseInlineElement
from .types import FlavorType

__all__ = [
    "InlineContainer",
    "BlockContainer",
]


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

    def __init__(
        self, *elements: BaseInlineElement | str, auto_space: bool = False
    ):
        def coerce(obj: str) -> BaseInlineElement:
            return coerce_inline_text(
                obj, allow_multiline=self._allow_multiline
            )

        self.__elements = norm_list(
            elements, BaseInlineElement, CoerceSpec(coerce, str)
        )
        self.__auto_space = auto_space

        self._inline_post_init()

    def _inline_post_init(self):
        """
        Optionally overridden by subclass to perform additional init.
        """

    def _render_elements(self, flavor: FlavorType) -> str:
        sep = " " if self.__auto_space else ""
        return sep.join(
            element._render_inline(flavor) for element in self.__elements
        )

    def _get_pandoc_extensions(self) -> set[str]:
        return (
            _aggregate_extensions(self.__elements)
            | super()._get_pandoc_extensions()
        )


class InlineContainer(InlineContainerMixin, BaseInlineElement):
    """
    Container for inline elements; wraps multiple inline elements in a single
    one.
    """

    def _render_inline(self, flavor: FlavorType) -> str:
        return self._render_elements(flavor)


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

    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield "\n\n".join(
            [
                "\n".join(element._render_block(flavor))
                for element in self.__elements
            ]
        )

    def _get_pandoc_extensions(self) -> set[str]:
        return (
            _aggregate_extensions(self.__elements)
            | super()._get_pandoc_extensions()
        )

    def _add_elements(self, elements: list[BaseBlockElement]):
        for element in elements:
            assert isinstance(element, BaseBlockElement)
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

    __level: int | None = None
    """
    Nesting level of this container.
    """

    __containers: list[BaseLevelBlockContainer]
    """
    List of nested containers; a subset of nested elements.
    """

    def __init__(self):
        super().__init__()
        self.__containers = []

    @property
    def _level(self) -> int:
        assert self.__level is not None
        return self.__level

    @_level.setter
    def _level(self, level: int):
        """
        Set level and propagate recursively.
        """
        assert self.__level is None
        self.__level = level

        for container in self.__containers:
            container._level = level + self._level_inc

    def _add_elements(self, elements: list[BaseBlockElement]):
        """
        Add elements to container and additionally bind them.
        """
        super()._add_elements(elements)

        for element in elements:

            # set element's container
            element._container = self

            # if element is also a block container, bind it
            if isinstance(element, BaseLevelBlockContainer):
                self.__bind_container(element)

    def __bind_container(self, container: BaseLevelBlockContainer):
        """
        Bind another container to this one.
        """
        self.__containers.append(container)

        # propagate level, if set
        if self.__level is not None:
            container._level = self.__level + self._level_inc


def _aggregate_extensions(elements: list[BaseElement]) -> set[str]:
    """
    Aggregate extensions from elements.
    """
    extensions: set[str] = set()
    for elem in elements:
        extensions |= elem._get_pandoc_extensions()
    return extensions
