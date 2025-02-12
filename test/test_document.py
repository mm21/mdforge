from pytest_powerpack import ComparisonFiles, compare_files

from mdforge import Document, Heading, List, ListItem, Paragraph, Section


def test_doc1(doc: Document):

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


def test_section(doc: Document):

    sec1 = Section("Section 1")
    sec1 += Paragraph("Hello, world!")

    sec11 = Section("Section 1-1")
    sec11 += List(["a", "b", "c"])
    sec1 += sec11

    sec2 = Section("Section 2")
    sec2 += Paragraph("Hello, world 2!")

    h3 = Heading("Heading 3")

    doc += [sec1, sec2, h3]


def test_frontmatter(powerpack_comparison_files: ComparisonFiles):

    frontmatter = {
        "title": "Doc 1",
    }

    doc = Document(
        frontmatter=frontmatter, elements=[Paragraph("Hello, world!")]
    )

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)
