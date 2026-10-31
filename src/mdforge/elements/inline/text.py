"""
Common inline elements.
"""

from __future__ import annotations

from ..._norm import CoerceSpec, norm_obj
from ...container import BaseBlockContainer, InlineContainerMixin
from ...element import Attributes, AttributesMixin, BaseInlineElement, RenderContext
from ...exceptions import RenderError, ValidationError
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

    def _render_inline(self, context: RenderContext) -> str:
        return self._render_elements(context)


class Text(BaseInlineElement):
    """
    Inline element containing a single string.
    """

    __text: str

    def __init__(self, text: str):

        if "\n" in text:
            raise ValidationError(f"Raw text may not span multiple lines: {text}")

        self.__text = text

    def _render_inline(self, context: RenderContext) -> str:
        return self.__text


class Emph(BaseTextContainer):

    def _render_inline(self, context: RenderContext) -> str:
        return f"_{super()._render_inline(context)}_"


class Strong(BaseTextContainer):

    def _render_inline(self, context: RenderContext) -> str:
        return f"**{super()._render_inline(context)}**"


class Underline(AttributesMixin, BaseTextContainer):

    def _inline_post_init(self):
        # add underline class, only relevant for pandoc flavor
        self._set_attrs(Attributes(css_classes="underline"))

    def _render_inline(self, context: RenderContext) -> str:
        return f"[{super()._render_inline(context)}]{self._get_attrs_str(context)}"

    def _get_pandoc_extensions(self) -> set[str]:
        return {"bracketed_spans"} | super()._get_pandoc_extensions()


class Strikethrough(BaseTextContainer):

    def _render_inline(self, context: RenderContext) -> str:
        return f"~~{super()._render_inline(context)}~~"

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
        self.__text._parent = self
        self.__url = url

    def _render_inline(self, context: RenderContext) -> str:
        return f"[{self.__text._render_inline(context)}]({self.__url})"


class Ref(BaseInlineElement):
    """
    Reference to a section's heading, given as a section with a title or the id of one.

    A section referenced by id is looked up upon rendering, so it must be rendered as
    part of the same element as the section, e.g. a document or a standalone section.

    TODO: support ref to arbitrary element w/id, e.g. paragraph
    """

    __target: Section | str
    """
    Section or id.
    """

    __text: str | None

    def __init__(self, target: Section | str, text: str | None = None):
        """
        :param target: Section with a title, or id of one
        :param text: Link text, defaults to section title
        """
        assert isinstance(target, (Section, str))

        if isinstance(target, str):
            self.__target = target.removeprefix("#")
        else:
            if not target._has_title:
                raise ValidationError(
                    f"Cannot reference section without title: {target}"
                )
            self.__target = target

        self.__text = text

    def _render_inline(self, context: RenderContext) -> str:

        if isinstance(self.__target, str):
            # explicit id, only need section for text
            text = self.__text or self.__lookup_section(
                context, self.__target
            )._render_title(context)
            return f"[{text}](#{self.__target})"

        title = self.__target._render_title(context)
        text = self.__text or title

        if self.__target._html_id:
            # explicit heading id
            return f"[{text}](#{self.__target._html_id})"
        else:
            # implicit heading id with implicit_header_references
            return f"[{text}][{title}]"

    def _get_pandoc_extensions(self) -> set[str]:
        return (
            {"implicit_header_references"}
            if isinstance(self.__target, Section) and not self.__target._html_id
            else set()
        ) | super()._get_pandoc_extensions()

    def __lookup_section(self, context: RenderContext, html_id: str) -> Section:
        """
        Get section with the given id from the element being rendered.
        """

        root = context.root
        elements = [root]
        if isinstance(root, BaseBlockContainer):
            elements += root._get_descendants()

        sections = [
            element
            for element in elements
            if isinstance(element, Section) and element._html_id == html_id
        ]

        if not sections:
            raise RenderError(
                f"No section found with id in rendered element: {html_id}"
            )
        if len(sections) > 1:
            raise RenderError(f"Multiple sections found with id: {html_id}")

        return sections[0]


class Newline(BaseInlineElement):
    """
    Element to represent a newline.

    Used for inline containers which allow multiple lines, e.g. paragraphs.
    """

    def _render_inline(self, context: RenderContext) -> str:
        return "\n"
