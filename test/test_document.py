from pytest import mark

from mdforge import Document, Heading, Paragraph, List


@mark.filename("doc-1.md")
def test_doc1(document_text: str):

    doc = Document()

    doc += Heading("Test document 1")
    doc += Paragraph("Hello, world!")
    doc += Heading("List", 2)
    doc += List(
        [
            "a",
            ["a1", ["a1-2"]],
            "b",
            ["b1", "b2"],
            "c",
            ["c1", "c2", "c3"],
        ]
    )

    text = doc.render_text()

    assert document_text == text
