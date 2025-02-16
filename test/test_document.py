from pytest import mark

from mdforge import BulletList, Document, Heading, ListItem, Paragraph, Section

from .conftest import unused


def test_doc1(doc: Document):

    doc += Heading("Test document 1")
    doc += Paragraph("Hello, world!")
    doc += Heading("Bullet list", 2)
    doc += BulletList(
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


def test_section(doc: Document):

    sec1 = Section("Section 1")
    sec1 += Paragraph("Hello, world!")

    sec11 = Section("Section 1-1")
    sec11 += BulletList(["a", "b", "c"])
    sec1 += sec11

    sec2 = Section("Section 2")
    sec2 += Paragraph("Hello, world 2!")

    h3 = Heading("Heading 3")

    doc += [sec1, sec2, h3]


@mark.frontmatter({"title": "Doc 1"})
@mark.elements([(Paragraph, ("Hello, world!",), {})])
def test_frontmatter(doc: Document):
    unused(doc)
