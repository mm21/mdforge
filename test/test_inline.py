from mdforge import (
    Document,
    Emph,
    Link,
    Paragraph,
    Strikethrough,
    Strong,
    Underline,
)


def test_composition(doc: Document):
    """
    Test composition of inline elements.
    """

    doc += Paragraph("Hello, ", Emph("world"), "!")
    doc += Paragraph(Strong(Underline("Strong w/underline!")))
    doc += Paragraph(Emph(Strikethrough("Emph w/strikethrough!")))


def test_link(doc: Document):
    """
    Test link.
    """

    doc += Paragraph(Link("Test link", "https://github.com/"))
    doc += Paragraph(Link(Strong("Test link w/strong"), "https://github.com/"))
