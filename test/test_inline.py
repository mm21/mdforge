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


def test_composition(doc: Document):
    """
    Test composition of inline elements.
    """

    doc += Paragraph("Hello, ", Emph("world"), "!")
    doc += Strong(Underline("Strong w/underline!"))
    doc += Emph(Strikethrough("Emph w/strikethrough!"))


def test_link(doc: Document):
    """
    Test external link.
    """

    doc += Link("Test link", "https://github.com/")
    doc += Link(Strong("Test link w/strong"), "https://github.com/")


def test_span(doc: Document):
    """
    Test span with composition.
    """

    doc += Span(
        "Test span with ",
        Strong("strong text"),
        attributes=Attributes(html_id="span1", css_classes="class1"),
    )
