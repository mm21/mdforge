"""
Base element functionality.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
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

    __container: BaseLevelBlockContainer | None = None
    """
    Container to which this element belongs. Must be added to a container in
    order to be rendered in output.
    """

    @abstractmethod
    def _render_element(
        self, flavor: BaseElement
    ) -> Generator[str, None, None]:
        """
        Render this element, agnostic of concrete class.
        """
        ...

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

    def _render_block_lines(self, flavor: FlavorType) -> str:
        """
        Render as multi-line string.
        """
        return "\n".join(self._render_block(flavor))


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

    attrs: dict[str, str] | None = None
    """
    Other attributes, either native HTML attributes or specific to pandoc.
    """

    css_classes: str | list[str] | None = None
    """
    One or more CSS classes.
    """

    @property
    def _is_empty(self) -> bool:
        return not (self.html_id or self.attrs or self.css_classes)

    @property
    def _css_classes_norm(self) -> list[str] | None:
        return norm_list(self.css_classes, str) if self.css_classes else None

    def _copy(
        self,
        *,
        attrs: dict[str, str] | None = None,
        css_classes: str | list[str] | None = None,
    ) -> Attributes:
        """
        Copy attributes, updating with the provided values.
        """

        orig_attrs, orig_css_classes = self.attrs, self._css_classes_norm

        merged_attrs = orig_attrs.copy() if orig_attrs else {}
        merged_css_classes = orig_css_classes.copy() if orig_css_classes else []

        if attrs:
            merged_attrs.update(**attrs)

        if css_classes:
            merged_css_classes += norm_list(css_classes, str)

        return Attributes(
            html_id=self.html_id,
            attrs=merged_attrs,
            css_classes=merged_css_classes,
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
        attributes = self.__attributes
        if flavor != "pandoc" or attributes is None or attributes._is_empty:
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
