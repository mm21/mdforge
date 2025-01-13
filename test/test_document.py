from pytest import mark
from pytest_powerpack import ComparisonFiles, compare_files

from mdforge import Document, Heading, List, ListItem, Paragraph, Section, Table


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

    align = ["left", "center", "right", "default"]
    header = [
        f"Header {col_idx},\nalign: {align[col_idx]}"
        for col_idx in range(col_count)
    ]
    footer = [f"Footer\n{col_idx}" for col_idx in range(col_count)]
    rows: list[list[str]] = []

    for row_idx in range(row_count):
        rows.append(
            [f"Cell\n{row_idx}-{col_idx}" for col_idx in range(col_count)]
        )

    inline_section, block_section = Section("Inline tables"), Section(
        "Block tables"
    )

    doc = Document(elements=[inline_section, block_section])

    def add_table(table: Table, dims: tuple[int, int], desc: str):

        # includes header and footer
        assert table._effective_dims == dims

        nonlocal inline_section
        nonlocal block_section

        section = block_section if table._block else inline_section
        section += Section(desc, elements=[table])

    for row_count_iter in [1, row_count]:

        for block in [False, True]:

            rows_iter = rows[0:row_count_iter]

            add_table(
                Table(rows_iter, align=align, block=block),
                (col_count, row_count_iter),
                f"No header or footer, {row_count_iter} rows",
            )
            add_table(
                Table(rows_iter, align=align, header=header, block=block),
                (col_count, row_count_iter + 1),
                f"With header, {row_count_iter} rows",
            )

            if block:
                add_table(
                    Table(rows_iter, align=align, footer=footer, block=block),
                    (col_count, row_count_iter + 1),
                    f"With footer, {row_count_iter} rows",
                )
                add_table(
                    Table(
                        rows_iter,
                        align=align,
                        header=header,
                        footer=footer,
                        block=block,
                    ),
                    (col_count, row_count_iter + 2),
                    f"With header and footer, {row_count_iter} rows",
                )

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)
