from pytest import mark
from pytest_powerpack import ComparisonFiles, compare_files

from mdforge import Document, Section, Table

COL_COUNT = 4
ROW_COUNT = 3
ALIGN = ["left", "center", "right", "default"]
ROWS = [
    [f"Cell\n{row_idx}-{col_idx}" for col_idx in range(COL_COUNT)]
    for row_idx in range(ROW_COUNT)
]
HEADER = [
    f"Header {col_idx},\nalign: {ALIGN[col_idx]}"
    for col_idx in range(COL_COUNT)
]
FOOTER = [f"Footer\n{col_idx}" for col_idx in range(COL_COUNT)]
WIDTHS = [15 + col_idx for col_idx in range(COL_COUNT)]


@mark.powerpack_compare_file("doc.md")
def test_variants(powerpack_comparison_files: ComparisonFiles):
    """
    Test inline and block variants.
    """

    inline_section, block_section = Section("Inline tables"), Section(
        "Block tables"
    )

    doc = Document(elements=[inline_section, block_section])

    def add_table(table: Table, content_dims: tuple[int, int], desc: str):

        col_count, row_count = content_dims

        if header := table._params.header:
            row_count += len(header)

        if footer := table._params.footer:
            row_count += len(footer)

        # includes header and footer
        assert table._params.effective_dims == (col_count, row_count)

        nonlocal inline_section
        nonlocal block_section

        section = block_section if table._params.block else inline_section
        section += Section(desc, elements=[table])

    for row_count in [1, ROW_COUNT]:

        for block in [False, True]:

            rows = ROWS[0:row_count]

            add_table(
                Table(rows, align=ALIGN, block=block),
                (COL_COUNT, row_count),
                f"No header or footer, {row_count} rows",
            )
            add_table(
                Table(rows, align=ALIGN, header=HEADER, block=block),
                (COL_COUNT, row_count),
                f"With header, {row_count} rows",
            )

            if block:
                add_table(
                    Table(rows, align=ALIGN, footer=FOOTER, block=block),
                    (COL_COUNT, row_count),
                    f"With footer, {row_count} rows",
                )
                add_table(
                    Table(
                        rows,
                        align=ALIGN,
                        header=HEADER,
                        footer=FOOTER,
                        block=block,
                    ),
                    (COL_COUNT, row_count),
                    f"With header and footer, {row_count} rows",
                )

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)


@mark.powerpack_compare_file("doc.md")
def test_widths(powerpack_comparison_files: ComparisonFiles):
    """
    Test explicitly provided widths with no wrapping.
    """

    # omit width of last column to verify optional width
    widths = WIDTHS.copy()
    widths[-1] = None

    rows = [
        [f"{cell}, width={width}" for cell, width in zip(row, widths)]
        for row in ROWS
    ]

    doc = Document()

    for block in [False, True]:
        doc += [
            Section(f"Block: {block}"),
            Table(rows, header=HEADER, align=ALIGN, widths=widths, block=block),
        ]

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)


@mark.powerpack_compare_file("doc.md")
def test_wrap(powerpack_comparison_files: ComparisonFiles):
    """
    Test cell content wrapping when explicit widths are given.
    """

    rows = [
        [
            f"{cell}\nLorem ipsum dolor sit amet, width={width}"
            for cell, width in zip(row, WIDTHS)
        ]
        for row in ROWS
    ]

    doc = Document()

    for block in [False, True]:
        doc += [
            Section(f"Block: {block}"),
            Table(rows, header=HEADER, align=ALIGN, widths=WIDTHS, block=block),
        ]

    doc.render(powerpack_comparison_files.out_file)
    compare_files(powerpack_comparison_files)
