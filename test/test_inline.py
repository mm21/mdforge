from mdforge import (
    Attributes,
    Document,
    Emph,
    Link,
    Paragraph,
    Span,
    Strikethrough,
    Strong,
    Underline,
)

from .conftest import compare_doc


@compare_doc
def test_composition(doc: Document):
    """
    Test composition of inline elements.
    """

    doc += Paragraph("Hello, ", Emph("world"), "!")
    doc += Strong(Underline("Strong w/underline!"))
    doc += Emph(Strikethrough("Emph w/strikethrough!"))

    assert doc.get_pandoc_extensions() == ["strikeout"]


@compare_doc
def test_link(doc: Document):
    """
    Test external link.
    """

    doc += Link("Test link", "https://github.com/")
    doc += Link(Strong("Test link w/strong"), "https://github.com/")


@compare_doc
def test_span(doc: Document):
    """
    Test span with composition.
    """

    doc += Span(
        "Test span with ",
        Strong("strong text"),
        attributes=Attributes(html_id="span1", css_classes="class1"),
    )

    assert doc.get_pandoc_extensions() == ["bracketed_spans"]
