from pytest import mark
from pytest_powerpack import ComparisonFiles, compare_files

from mdforge import (
    BaseTable,
    BlockTable,
    Document,
    Heading,
    InlineTable,
    List,
    ListItem,
    Paragraph,
    Section,
)


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

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)


@mark.powerpack_compare_file("doc-1.md")
def test_section(powerpack_comparison_files: ComparisonFiles):

    sec1 = Section("Section 1")
    sec1 += Paragraph("Hello, world!")

    sec11 = Section("Section 1-1")
    sec11 += List(["a", "b", "c"])
    sec1 += sec11

    sec2 = Section("Section 2")
    sec2 += Paragraph("Hello, world 2!")

    h3 = Heading("Heading 3")

    doc = Document()
    doc += [sec1, sec2, h3]

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)


@mark.powerpack_compare_file("doc-1.md")
def test_frontmatter(powerpack_comparison_files: ComparisonFiles):

    frontmatter = {
        "title": "Doc 1",
    }

    doc = Document(frontmatter=frontmatter)
    doc += Paragraph("Hello, world!")

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)


@mark.powerpack_compare_file("doc-1.md")
def test_tables(powerpack_comparison_files: ComparisonFiles):

    col_count = 3
    row_count = 3

    header = [f"Header {col_idx}" for col_idx in range(col_count)]
    rows: list[list[str]] = []

    for row_idx in range(row_count):
        rows.append(
            [f"Cell {row_idx}-{col_idx}" for col_idx in range(col_count)]
        )

    def check_table(table: BaseTable):

        # size includes header
        assert table._size == (col_count, row_count + 1)

    doc = Document()

    inline_table = InlineTable(
        rows,
        header=header,
        align="center",
    )
    check_table(inline_table)

    doc += Section(
        "Inline table",
        elements=[inline_table],
    )

    block_table = BlockTable(
        rows,
        header=header,
        align="center",
    )
    check_table(block_table)

    doc += Section(
        "Block table",
        elements=[block_table],
    )

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)
