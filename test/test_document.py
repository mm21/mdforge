from pytest import mark
from pytest_powerpack import ComparisonFiles, compare_files

from mdforge import Document, Heading, Paragraph, List, ListItem


@mark.powerpack_compare_file("doc-1.md")
def test_doc1(powerpack_comparison_files: ComparisonFiles):

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

    doc.render(powerpack_comparison_files.build_file)
    compare_files(powerpack_comparison_files)
