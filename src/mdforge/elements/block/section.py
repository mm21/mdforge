"""
Section element to encapsulate user-defined sections with optional heading.
"""

from __future__ import annotations

from typing import Generator, Iterable

from ..._norm import CoerceSpec, norm_obj
from ...container import BaseLevelBlockContainer
from ...element import (
    Attributes,
    AttributesMixin,
    BaseElement,
    BaseInlineElement,
    RenderContext,
)
from ...exceptions import ValidationError

__all__ = [
    "Section",
]


class Section(AttributesMixin, BaseLevelBlockContainer):
    """
    Encapsulates a logical document section, containing block elements with an optional
    title rendered as its heading, e.g. `# My section`.

    Level is inferred by this section's nesting; nested sections are placed at the next
    level.
    """

    __title: BaseInlineElement | None = None

    def __init__(
        self,
        title: BaseInlineElement | str | None = None,
        *,
        html_id: str | None = None,
        attributes: Attributes | None = None,
        elements: BaseElement | str | Iterable[BaseElement | str] | None = None,
    ):
        """
        :param title: Title rendered as heading, or `None` for a section without heading
        :param html_id: HTML id of heading, used as the target of references; shorthand for `attributes.html_id`
        :param attributes: HTML attributes of heading
        :param elements: Elements to add
        """
        from ..inline.text import Text

        super().__init__()

        if title is None and (html_id is not None or attributes):
            raise ValidationError(
                f"Section html_id/attributes require a title: html_id={html_id}, attributes={attributes}"
            )

        if html_id is not None:
            if attributes and attributes.html_id not in (None, html_id):
                raise ValidationError(
                    f"Conflicting ids: html_id={html_id}, attributes.html_id={attributes.html_id}"
                )
            attributes = (
                attributes._copy(html_id=html_id)
                if attributes
                else Attributes(html_id=html_id)
            )

        if title is not None:
            self.__title = norm_obj(title, BaseInlineElement, CoerceSpec(Text, str))
            self.__title._parent = self

        self._set_attrs(attributes)

        if elements:
            self += elements

    @property
    def _has_title(self) -> bool:
        return self.__title is not None

    def _render_title(self, context: RenderContext) -> str:
        """
        Render title as inline markdown.
        """
        assert self.__title is not None
        return self.__title._render_inline(context)

    def _render_block(self, context: RenderContext) -> Generator[str, None, None]:
        blocks: list[str] = []

        if self.__title is not None:
            level = self._get_level()
            attrs = self._get_attrs_str(context, space_prefix=True)
            blocks.append(f"{'#' * level} {self._render_title(context)}{attrs}")

        if content := "\n".join(super()._render_block(context)):
            blocks.append(content)

        yield "\n\n".join(blocks)

    def _get_pandoc_extensions(self) -> set[str]:
        title_extensions = (
            self.__title._get_pandoc_extensions() if self.__title else set()
        )
        attrs_extensions = {"header_attributes"} if self._has_attrs else set()
        return title_extensions | attrs_extensions | super()._get_pandoc_extensions()
