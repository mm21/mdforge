from mdforge import Document, Emph, Paragraph, Strikethrough, Strong, Underline


def test_composition(doc: Document):
    """
    Test composition of inline elements.
    """

    doc += Paragraph("Hello, ", Emph("world"), "!")
    doc += Paragraph(Strong(Underline("Strong w/underline!")))
    doc += Paragraph(Emph(Strikethrough("Emph w/strikethrough!")))
