from mdforge import (
    BlockContainer,
    BulletList,
    Cell,
    Document,
    Heading,
    Paragraph,
    Section,
    Table,
)

from .conftest import compare_doc

ROW_COUNT = 3
COL_COUNT = 4
ALIGN = ["left", "center", "right", "default"]
ROWS = [
    [f"Cell\n{row_idx}-{col_idx}" for col_idx in range(COL_COUNT)]
    for row_idx in range(ROW_COUNT)
]
HEADER = [f"Header {col_idx},\nalign: {ALIGN[col_idx]}" for col_idx in range(COL_COUNT)]
FOOTER = [f"Footer\n{col_idx}" for col_idx in range(COL_COUNT)]
WIDTHS = [15 + col_idx for col_idx in range(COL_COUNT)]


@compare_doc
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

    assert doc.get_pandoc_extensions() == [
        "grid_tables",
        "multiline_tables",
    ]


@compare_doc
def test_widths(doc: Document):
    """
    Test explicitly provided widths with no wrapping.
    """

    rows = [
        [f"{cell}, width={width}" for cell, width in zip(row, WIDTHS)] for row in ROWS
    ]

    for block in [False, True]:
        doc += [
            Section(heading=f"Block: {block}"),
            Table(rows, header=HEADER, align=ALIGN, widths=WIDTHS, block=block),
        ]


@compare_doc
def test_widths_pct(doc: Document):
    """
    Test explicitly provided width percents with no wrapping.
    """

    # simple case: first cell width is exactly half of second cell width,
    # target 50/50 widths
    doc += [
        Heading("Simple case"),
        Table([["Cell 0-0", "Cell 0-1 aaaaaaa"]], widths_pct=[50, 50], block=True),
    ]

    widths_pct = [10 * (i + 1) for i in range(len(WIDTHS) - 1)]
    widths_pct.append(100 - sum(widths_pct))
    assert sum(widths_pct) == 100

    rows = [
        [
            f"{cell} {'a'*(cell_idx+1)*5}, width_pct={width_pct}"
            for cell, cell_idx, width_pct in zip(row, range(COL_COUNT), widths_pct)
        ]
        for row in ROWS
    ]

    doc += [
        Heading("Complex case"),
        Table(rows, widths_pct=widths_pct, block=True),
    ]

    assert doc.get_pandoc_extensions() == ["grid_tables"]


@compare_doc
def test_wrap(doc: Document):
    """
    Test cell content wrapping when explicit widths are given.

    Also tests captions.
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

    assert doc.get_pandoc_extensions() == [
        "grid_tables",
        "multiline_tables",
        "table_captions",
    ]


@compare_doc
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
            Cell("Test cspan and rspan abc\n0123456789abcdef", cspan=2, rspan=2),
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

    # test table where a cell spans multiple rows, but content ends immediately
    # before dangling line (boundary between virtual cells)
    # - also test a single alignment applied to all columns
    doc += Table(
        [
            [Cell("Test 0-0\nabc", rspan=2), "Test 0-1\nabc"],
            ["Test 1-1"],
            ["Test 2-0", "Test 2-1"],
        ],
        align="center",
        block=True,
    )

    doc += Table(
        [
            [
                "Test 0-0",
                "Test 0-1",
                Cell("Test 0-2", rspan=2),
                Cell("Test 0-3", rspan=3),
            ],
            ["Test 1-0", "Test 1-1"],
            ["Test 2-0", "Test 2-1", "Test 2-2"],
        ],
        widths=[15, 16, 17, 18],
        block=True,
    )


@compare_doc
def test_loose(doc: Document):
    """
    Test table with loose=True, inserting paragraphs for non-block elements for
    consistent spacing.
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
