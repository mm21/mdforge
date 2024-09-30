from pytest import mark

from mdforge import Document, Heading, Paragraph, List, ListItem


@mark.filename("doc-1.md")
def test_doc1(document_text: str):

    doc = Document()

    doc += Heading("Test document 1")
    doc += Paragraph("Hello, world!")
    doc += Heading("List", 2)
    doc += List(
        [
            "a",
            ListItem(
                "b",
                [
                    "b1",
                    "b2",
                ],
            ),
            ListItem(
                "c",
                [
                    ListItem(
                        "c1",
                        [
                            "c1-1",
                        ],
                    ),
                    "c2",
                ],
            ),
        ]
    )

    text = doc.render_text()

    assert document_text == text
