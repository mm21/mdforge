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

    col_count = 4
    row_count = 3

    header = [f"Header\n{col_idx}" for col_idx in range(col_count)]
    footer = [f"Footer\n{col_idx}" for col_idx in range(col_count)]
    align = ["left", "center", "right", "default"]
    rows: list[list[str]] = []

    for row_idx in range(row_count):
        rows.append(
            [f"Cell\n{row_idx}-{col_idx}" for col_idx in range(col_count)]
        )

    inline_section, block_section = Section("Inline tables"), Section(
        "Block tables"
    )

    doc = Document(elements=[inline_section, block_section])

    def add_table(table: BaseTable, dims: tuple[int, int], desc: str):

        # includes header and footer
        assert table._effective_dims == dims

        nonlocal inline_section
        nonlocal block_section

        section = (
            inline_section if isinstance(table, InlineTable) else block_section
        )
        section += Section(desc, elements=[table])

    table_classes: list[type[BaseTable]] = [InlineTable, BlockTable]

    for table_cls in table_classes:

        add_table(
            table_cls(rows, align=align),
            (col_count, row_count),
            "No header or footer",
        )
        add_table(
            table_cls(rows, align=align, header=header),
            (col_count, row_count + 1),
            "With header",
        )

        if issubclass(table_cls, BlockTable):
            add_table(
                table_cls(rows, align=align, footer=footer),
                (col_count, row_count + 1),
                "With footer",
            )
            add_table(
                table_cls(rows, align=align, header=header, footer=footer),
                (col_count, row_count + 2),
                "With header and footer",
            )

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)
