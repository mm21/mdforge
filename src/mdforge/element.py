"""
Base element functionality.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Mapping, Sequence

from ._norm import norm_list
from .exceptions import ValidationError
from .types import FlavorType

if TYPE_CHECKING:
    from .container import BaseBlockContainer

__all__ = [
    "BaseElement",
    "BaseInlineElement",
    "BaseBlockElement",
    "Attributes",
]


class BaseNode:
    """
    Node in a document tree, either an element or an object which holds elements like a
    list item or table cell.

    Each node references its parent once placed, which happens when the parent is
    constructed or when the node is added to a container.
    """

    _content_location: str | None = None
    """
    Description of the location of content held by this node if it can't contain
    sections, e.g. "table cells".
    """

    __parent: BaseNode | None = None

    @property
    def _parent(self) -> BaseNode | None:
        return self.__parent

    @_parent.setter
    def _parent(self, parent: BaseNode):
        """
        Place this node in the given parent, validating the placement.
        """
        if self.__parent is not None:
            raise ValidationError(
                f"Element has already been placed in {self.__parent}: {self}"
            )
        self._validate_parent(parent)
        self.__parent = parent

    def _validate_parent(self, parent: BaseNode):
        """
        Optionally overridden by subclass to validate placement in the given parent.
        """

    def _get_ancestors(self) -> Generator[BaseNode, None, None]:
        """
        Get this node's ancestors, starting with its parent.
        """
        node = self.__parent
        while node is not None:
            yield node
            node = node._parent

    def _get_content_location(self) -> str | None:
        """
        Get the location of this node if it's in content which can't contain sections,
        e.g. "table cells".
        """
        for node in [self, *self._get_ancestors()]:
            if node._content_location:
                return node._content_location
        return None


@dataclass(frozen=True, kw_only=True)
class RenderContext:
    """
    Context passed to elements upon rendering.
    """

    flavor: FlavorType
    """
    Markdown flavor to render.
    """

    root: BaseElement
    """
    Element being rendered, e.g. a document or a standalone section, used to resolve
    references.
    """


class BaseElement(BaseNode, ABC):
    """
    Base renderable markdown element, which may be a container of other elements.

    Must be added to a container in order to be rendered in a document, but otherwise
    can still be rendered standalone.
    """

    def render(self, *, flavor: FlavorType) -> str:
        """
        Return element as a string using the provided flavor.
        """
        context = RenderContext(flavor=flavor, root=self)
        return "\n".join(self._render_element(context))

    def render_file(self, path: Path | str, *, flavor: FlavorType):
        """
        Write Markdown document using the provided flavor to the provided file.
        """
        path_norm = path if isinstance(path, Path) else Path(path)
        with path_norm.open("w") as fh:
            fh.write(self.render(flavor=flavor))

    def get_pandoc_extensions(self) -> list[str]:
        """
        Get a list of extensions required to convert the resulting markdown document in
        pandoc, assuming pandoc flavor is used for rendering.
        """
        return sorted(self._get_pandoc_extensions())

    @abstractmethod
    def _render_element(self, context: RenderContext) -> Generator[str, None, None]:
        """
        Render this element, agnostic of concrete class.
        """
        ...

    def _get_pandoc_extensions(self) -> set[str]:
        """
        Get required pandoc extensions, recursing into nested elements.
        """
        return set()

    def _render_element_norm(
        self, context: RenderContext
    ) -> Generator[str, None, None]:
        """
        Render this element, splitting any newlines embedded in content and stripping
        whitespace.
        """
        yield from "\n".join(self._render_element(context)).strip().split("\n")

    @property
    def _container(self) -> BaseBlockContainer:
        """
        Get the block container in which this element was placed.
        """
        from .container import BaseBlockContainer

        parent = self._parent
        assert isinstance(
            parent, BaseBlockContainer
        ), f"Element has not been placed in a container: {self}"
        return parent


class BaseInlineElement(BaseElement):
    """
    Base inline element, rendering a single string.
    """

    @abstractmethod
    def _render_inline(self, context: RenderContext) -> str:
        """
        Render by returning a single string.
        """
        ...

    def _render_element(self, context: RenderContext) -> Generator[str, None, None]:
        yield self._render_inline(context)


class BaseBlockElement(BaseElement):
    """
    Base block element, rendering multiple strings.
    """

    @abstractmethod
    def _render_block(self, context: RenderContext) -> Generator[str, None, None]:
        """
        Render by yielding each line.
        """
        ...

    def _render_element(self, context: RenderContext) -> Generator[str, None, None]:
        yield from self._render_block(context)


@dataclass(kw_only=True)
class Attributes:
    """
    HTML attributes which can be associated with some elements.

    Only applicable to pandoc flavor.
    """

    html_id: str | None = None
    """
    HTML id to associate with this element.
    """

    css_classes: str | Sequence[str] | None = None
    """
    One or more CSS classes.
    """

    attrs: Mapping[str, str] | None = None
    """
    Other attributes, either native HTML attributes or specific to pandoc.
    """

    def __bool__(self) -> bool:
        return any([self.html_id, self.css_classes, self.attrs])

    @property
    def _css_classes_norm(self) -> list[str] | None:
        """
        Get CSS classes normalized as a list.
        """
        return norm_list(self.css_classes, str) if self.css_classes else None

    def _copy(
        self,
        *,
        html_id: str | None = None,
        css_classes: str | Sequence[str] | None = None,
        attrs: Mapping[str, str] | None = None,
    ) -> Attributes:
        """
        Copy attributes object, updating id if given and merging CSS classes and other
        attributes.
        """

        css_classes_norm = self._css_classes_norm
        merged_css_classes = css_classes_norm.copy() if css_classes_norm else []

        merged_attrs = dict(self.attrs) if self.attrs else {}

        if css_classes:
            merged_css_classes += norm_list(css_classes, str)

        if attrs:
            merged_attrs.update(**attrs)

        return Attributes(
            html_id=html_id or self.html_id,
            css_classes=merged_css_classes,
            attrs=merged_attrs,
        )


class AttributesMixin:
    """
    Mixin to facilitate adding HTML attributes.

    Only supported for pandoc flavor.
    """

    __attributes: Attributes | None = None

    @property
    def _html_id(self) -> str | None:
        """
        Get html_id if set.
        """
        return self.__attributes.html_id if self.__attributes else None

    @property
    def _has_attrs(self) -> bool:
        """
        Whether this element has attributes.
        """
        return bool(self.__attributes)

    def _set_attrs(self, attributes: Attributes | None):
        """
        Set HTML attributes.
        """
        self.__attributes = attributes

    def _get_attrs_str(
        self,
        context: RenderContext,
        space_prefix: bool = False,
        space_suffix: bool = False,
    ) -> str:
        """
        Get string representing attributes, optionally prefixed with a space.

        For pandoc flavor only.
        """

        attributes = self.__attributes

        # return if not applicable or no attributes set
        if context.flavor != "pandoc" or not attributes:
            return ""

        parts: list[str] = []

        if attributes.html_id:
            parts.append(f"#{attributes.html_id}")
        if css_classes := attributes._css_classes_norm:
            parts += [f".{css_class}" for css_class in css_classes]
        if attributes.attrs:
            parts += [f'{k}="{v}"' for k, v in attributes.attrs.items()]

        parts_str = "{" + " ".join(parts) + "}"
        prefix = " " if space_prefix else ""
        suffix = " " if space_suffix else ""

        return f"{prefix}{parts_str}{suffix}"
