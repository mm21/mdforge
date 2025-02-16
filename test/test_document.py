from pytest import mark

from mdforge import (
    BulletList,
    Document,
    Emph,
    Heading,
    ListItem,
    NumberedList,
    Paragraph,
    Section,
    Strong,
)

from .conftest import unused


def test_doc1(doc: Document):

    doc += Heading("Test document 1")
    doc += Paragraph("Hello, world!")
    doc += Heading("Bullet list", 2)
    doc += BulletList(
        [
            "a",
            ListItem(
                Strong("b (strong)"),
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
            ListItem(
                "d",
                NumberedList(
                    [
                        "d1",
                        "d2",
                        ListItem(
                            "d3",
                            [
                                "d3-1",
                                "d3-2",
                                "d3-3",
                            ],
                        ),
                    ]
                ),
            ),
        ]
    )

    doc += Heading("Numbered list", 2)
    doc += NumberedList(
        [
            Emph("a (emph)"),
            ListItem("b", ["b1", "b2", "b3"]),
            ListItem(
                "c",
                BulletList(
                    ["c1", "c2", ListItem("c3", ["c3-1", "c3-2", "c3-3"])]
                ),
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
