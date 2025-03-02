from mdforge import (
    BlockContainer,
    BulletList,
    Cell,
    Document,
    Paragraph,
    Section,
    Table,
)

ROW_COUNT = 3
COL_COUNT = 4
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


def test_variants(doc: Document):
    """
    Test inline and block variants.
    """

    inline_section, block_section = Section(heading="Inline tables"), Section(
        heading="Block tables"
    )

    doc += [inline_section, block_section]

    def add_table(table: Table, content_dims: tuple[int, int], desc: str):

        content_row_count, col_count = content_dims
        header_row_count = (
            len(table._params.header_rows) if table._params.header_rows else 0
        )
        footer_row_count = (
            len(table._params.footer_rows) if table._params.footer_rows else 0
        )

        assert table._params.content_row_count == content_row_count
        assert table._params.col_count == col_count
        assert table._params.header_row_count == header_row_count
        assert table._params.footer_row_count == footer_row_count

        nonlocal inline_section
        nonlocal block_section

        section = block_section if table._params.block else inline_section
        section += Section(desc, elements=table)

    for row_count in [1, ROW_COUNT]:

        for block in [False, True]:

            rows = ROWS[0:row_count]

            add_table(
                Table(rows, align=ALIGN, block=block),
                (row_count, COL_COUNT),
                f"No header or footer, {row_count} rows",
            )
            add_table(
                Table(rows, align=ALIGN, header=HEADER, block=block),
                (row_count, COL_COUNT),
                f"With header, {row_count} rows",
            )

            if block:
                add_table(
                    Table(rows, align=ALIGN, footer=FOOTER, block=block),
                    (row_count, COL_COUNT),
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
                    (row_count, COL_COUNT),
                    f"With header and footer, {row_count} rows",
                )


def test_widths(doc: Document):
    """
    Test explicitly provided widths with no wrapping.
    """

    rows = [
        [f"{cell}, width={width}" for cell, width in zip(row, WIDTHS)]
        for row in ROWS
    ]

    for block in [False, True]:
        doc += [
            Section(heading=f"Block: {block}"),
            Table(rows, header=HEADER, align=ALIGN, widths=WIDTHS, block=block),
        ]


def test_wrap(doc: Document):
    """
    Test cell content wrapping when explicit widths are given. Also tests
    captions.
    """

    rows = [
        [
            f"{cell}\nLorem ipsum dolor sit amet, width={width}"
            for cell, width in zip(row, WIDTHS)
        ]
        for row in ROWS
    ]

    for block in [False, True]:
        doc += Table(
            rows,
            header=HEADER,
            align=ALIGN,
            widths=WIDTHS,
            caption=f"Block: {block}",
            block=block,
        )


def test_span(doc: Document):
    """
    Test cell spanning.
    """

    ROW_COUNT = 7
    COL_COUNT = 3

    rows = [
        [Cell(content="Test cspan", cspan=2), "Test 0-2"],
        [
            Cell(
                content="Test rspan\nTest abc\nTest def\nTest ghi\nTest jkl",
                rspan=2,
            ),
            "Test 1-1\nabc",
            "Test 1-2",
        ],
        ["Test 2-1", "Test 2-2"],
        [
            Cell(
                "Test cspan and rspan abc\n0123456789abcdef", cspan=2, rspan=2
            ),
            "Test 3-2",
        ],
        [Cell("Test 4-2\nand\nTest 5-2", rspan=2)],
        [Cell("Test 5-0 and Test 5-1\nabc", cspan=2)],
        ["Test 6-0", "Test 6-1", "Test 6-2"],
    ]

    table = Table(rows, block=True)

    assert table._params.content_row_count == ROW_COUNT
    assert table._params.col_count == COL_COUNT

    doc += table


def test_loose(doc: Document):
    """
    Test table with loose=True, inserting paragraphs for non-block elements
    for consistent spacing.
    """

    ROW_COUNT = 3

    rows = [
        [
            Cell(f"Test\ntext {row_idx}"),
            Cell(Paragraph(f"Test paragraph {row_idx}")),
            Cell(
                BlockContainer(
                    Paragraph(f"Test block {row_idx}"),
                    BulletList(["Item 1", "Item 2", "Item 3"]),
                )
            ),
        ]
        for row_idx in range(ROW_COUNT)
    ]

    doc += Table(rows, block=True, loose=True)
