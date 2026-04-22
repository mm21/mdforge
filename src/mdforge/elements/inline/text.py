"""
Common inline elements.
"""

from __future__ import annotations

from ..._norm import CoerceSpec, norm_obj
from ...container import InlineContainerMixin
from ...element import Attributes, AttributesMixin, BaseInlineElement
from ...exceptions import ValidationError
from ...types import FlavorType
from ..block.basic import Heading
from ..block.section import Section

__all__ = [
    "Text",
    "Emph",
    "Strong",
    "Underline",
    "Strikethrough",
    "Link",
    "Ref",
    "Newline",
]


class BaseTextContainer(InlineContainerMixin, BaseInlineElement):
    """
    Inline element containing text or a list of inline elements.
    """

    def _render_inline(self, flavor: FlavorType) -> str:
        return self._render_elements(flavor)


class Text(BaseInlineElement):
    """
    Inline element containing a single string.
    """

    __text: str

    def __init__(self, text: str):

        if "\n" in text:
            raise ValidationError(
                f"Raw text may not span multiple lines: {text}"
            )

        self.__text = text

    def _render_inline(self, _: FlavorType) -> str:
        return self.__text


class Emph(BaseTextContainer):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"_{super()._render_inline(flavor)}_"


class Strong(BaseTextContainer):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"**{super()._render_inline(flavor)}**"


class Underline(AttributesMixin, BaseTextContainer):

    def _inline_post_init(self):
        # add underline class, only relevant for pandoc flavor
        self._set_attrs(Attributes(css_classes="underline"))

    def _render_inline(self, flavor: FlavorType) -> str:
        return (
            f"[{super()._render_inline(flavor)}]{self._get_attrs_str(flavor)}"
        )

    def _get_pandoc_extensions(self) -> set[str]:
        return {"bracketed_spans"} | super()._get_pandoc_extensions()


class Strikethrough(BaseTextContainer):

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"~~{super()._render_inline(flavor)}~~"

    def _get_pandoc_extensions(self) -> set[str]:
        return {"strikeout"} | super()._get_pandoc_extensions()


class Link(BaseInlineElement):
    """
    Link to webpage.
    """

    __text: BaseInlineElement
    __url: str

    def __init__(self, text: BaseInlineElement | str, url: str):
        self.__text = norm_obj(text, BaseInlineElement, CoerceSpec(Text, str))
        self.__url = url

    def _render_inline(self, flavor: FlavorType) -> str:
        return f"[{self.__text._render_inline(flavor)}]({self.__url})"


class Ref(BaseInlineElement):
    """
    Reference to a heading within the same document.

    TODO: support ref to arbitrary element w/id, e.g. paragraph
    """

    __target: Heading
    __text: str | None

    def __init__(self, target: Heading | Section, text: str | None = None):
        assert isinstance(target, (Heading, Section))

        self.__target = (
            target if isinstance(target, Heading) else target._heading
        )
        self.__text = text

    def _render_inline(self, _: FlavorType) -> str:

        text = self.__text or self.__target._text

        if self.__target._html_id:
            # explicit heading id
            return f"[{text}](#{self.__target._html_id})"
        else:
            # implicit heading id with implicit_header_references
            return f"[{text}][{self.__target._text}]"

    def _get_pandoc_extensions(self) -> set[str]:
        return (
            {"implicit_header_references"}
            if not self.__target._html_id
            else set()
        ) | super()._get_pandoc_extensions()


class Newline(BaseInlineElement):
    """
    Element to represent a newline. Used for inline containers which allow
    multiple lines, e.g. paragraphs.
    """

    def _render_inline(self, _: FlavorType) -> str:
        return "\n"
