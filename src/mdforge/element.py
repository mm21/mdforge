"""
Base element functionality.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Generator

from ._norm import norm_list
from .types import FlavorType

if TYPE_CHECKING:
    from .container import BaseLevelBlockContainer

__all__ = [
    "BaseElement",
    "BaseInlineElement",
    "BaseBlockElement",
    "Attributes",
]


class BaseElement(ABC):
    """
    Base renderable markdown element, which may be a container of other
    elements.
    """

    __container: BaseLevelBlockContainer | None = None
    """
    Container to which this element belongs. Must be added to a container in
    order to be rendered in a document, but otherwise can still be rendered
    standalone.
    """

    def render(self, *, flavor: FlavorType) -> str:
        """
        Return element as a string using the provided flavor.
        """
        return "\n".join(self._render_element(flavor))

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

    @abstractmethod
    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
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
        self, flavor: FlavorType
    ) -> Generator[str, None, None]:
        """
        Render this element, splitting any newlines embedded in content and
        stripping whitespace.
        """
        yield from "\n".join(self._render_element(flavor)).strip().split("\n")

    @property
    def _container(self) -> BaseLevelBlockContainer:
        assert (
            self.__container
        ), f"Element has not been placed in a container: {self}"
        return self.__container

    @_container.setter
    def _container(self, container: BaseLevelBlockContainer):
        assert self.__container is None
        self.__container = container


class BaseInlineElement(BaseElement):
    """
    Base inline element, rendering a single string.
    """

    @abstractmethod
    def _render_inline(self, flavor: FlavorType) -> str:
        """
        Render by returning a single string.
        """
        ...

    def _render_element(
        self, flavor: BaseElement
    ) -> Generator[str, None, None]:
        yield self._render_inline(flavor)


class BaseBlockElement(BaseElement):
    """
    Base block element, rendering multiple strings.
    """

    @abstractmethod
    def _render_block(self, flavor: FlavorType) -> Generator[str, None, None]:
        """
        Render by yielding each line.
        """
        ...

    def _render_element(self, flavor: FlavorType) -> Generator[str, None, None]:
        yield from self._render_block(flavor)


@dataclass(kw_only=True)
class Attributes:
    """
    HTML attributes which can be associated with some elements. Only applicable
    to pandoc flavor.
    """

    html_id: str | None = None
    """
    HTML id to associate with this element.
    """

    css_classes: str | list[str] | None = None
    """
    One or more CSS classes.
    """

    attrs: dict[str, str] | None = None
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
        css_classes: str | list[str] | None = None,
        attrs: dict[str, str] | None = None,
    ) -> Attributes:
        """
        Copy attributes object, updating CSS attributes.
        """

        css_classes_norm = self._css_classes_norm
        merged_css_classes = css_classes_norm.copy() if css_classes_norm else []

        merged_attrs = self.attrs.copy() if self.attrs else {}

        if css_classes:
            merged_css_classes += norm_list(css_classes, str)

        if attrs:
            merged_attrs.update(**attrs)

        return Attributes(
            html_id=self.html_id,
            css_classes=merged_css_classes,
            attrs=merged_attrs,
        )


class AttributesMixin:
    """
    Mixin to facilitate adding HTML attributes. Only supported for pandoc
    flavor.
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
        flavor: FlavorType,
        space_prefix: bool = False,
        space_suffix: bool = False,
    ) -> str:
        """
        Get string representing attributes, optionally prefixed with a space.
        For pandoc flavor only.
        """

        # return if not applicable or no attributes set
        if flavor != "pandoc" or not self._has_attrs:
            return ""

        parts: list[str] = []

        attributes = self.__attributes
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
