"""
Examples used in readme.
"""

from pytest import FixtureRequest, mark
from pytest_powerpack import ComparisonFiles

from mdforge.container import BlockContainer

from .conftest import render_doc


@mark.powerpack_compare_file("doc.md")
def test_getting_started(
    request: FixtureRequest, powerpack_comparison_files: ComparisonFiles
):
    from mdforge import Document, Heading, Paragraph, Strong

    # create a document
    doc = Document()

    # add elements
    doc += [
        Heading("My first MDForge document"),
        Paragraph("Hello, ", Strong("world"), "!"),
    ]

    render_doc(doc, request, powerpack_comparison_files)


@mark.powerpack_compare_file("doc.md")
def test_working_with_documents(
    request: FixtureRequest, powerpack_comparison_files: ComparisonFiles
):
    from mdforge import BulletList, Document, Section

    # create a document with frontmatter
    doc = Document(frontmatter={"title": "My Document", "author": "Me"})

    # create sections, automatically adding headings of the appropriate level
    intro = Section("Introduction")
    intro += "This is an introduction paragraph."

    key_points = Section("Key Points")
    key_points += BulletList(["Point 1", "Point 2", "Point 3"])

    # add subsections for each point
    key_points += [
        Section(
            "Point 1",
            elements=[
                "Elaboration on point 1:",
                BulletList(["Point 1-a", "Point 1-b"]),
            ],
        ),
        Section("Point 2", elements=["Elaboration on point 2."]),
        Section("Point 3", elements=["Elaboration on point 3."]),
    ]

    doc += [intro, key_points]

    render_doc(doc, request, powerpack_comparison_files)


@mark.powerpack_compare_file("doc.md")
def test_formatting(
    request: FixtureRequest, powerpack_comparison_files: ComparisonFiles
):

    from mdforge import (
        Document,
        Emph,
        Paragraph,
        Strikethrough,
        Strong,
        Underline,
    )

    doc = Document()

    # basic formatting
    doc += Strong("Bold text")
    doc += Emph("Italicized text")
    doc += Strikethrough("Strikethrough text")
    doc += Underline("Underlined text")

    # combined formatting
    doc += Strong(Emph("Bold and italicized text"))

    # mixed formatting in a paragraph, automatically putting spaces between elements
    doc += Paragraph(
        "Normal text with",
        Strong("bold"),
        "and",
        Emph("italic"),
        "segments.",
        auto_space=True,
    )

    render_doc(doc, request, powerpack_comparison_files)


@mark.powerpack_compare_file("doc.md")
def test_lists(
    request: FixtureRequest, powerpack_comparison_files: ComparisonFiles
):
    from mdforge import (
        BulletList,
        DefinitionItem,
        DefinitionList,
        Document,
        ListItem,
        NumberedList,
    )

    doc = Document()

    # bullet list
    doc += BulletList(["Item 1", "Item 2", "Item 3"])

    # numbered list
    doc += NumberedList(["First", "Second", "Third"])

    # definition list
    doc += DefinitionList(
        [
            DefinitionItem("Term A", "Definition A"),
            DefinitionItem("Term B", ["Definition B1", "Definition B2"]),
        ],
        compact=True,
    )

    # nested lists
    doc += BulletList(
        [
            "Item 1",
            ListItem(
                "Item 2",
                [
                    "Item 2-1",
                    "Item 2-2",
                ],
            ),
        ]
    )

    # mixed nested lists
    doc += BulletList(
        [
            "Item 1",
            ListItem(
                "Item 2",
                NumberedList(
                    [
                        "Item 2-1",
                        "Item 2-2",
                    ]
                ),
            ),
        ]
    )

    render_doc(doc, request, powerpack_comparison_files)


@mark.powerpack_compare_file("doc.md")
def test_tables(
    request: FixtureRequest, powerpack_comparison_files: ComparisonFiles
):
    from mdforge import BulletList, Cell, Document, Table

    doc = Document()

    # simple table
    doc += Table(
        [
            ["Cell 1-1", "Cell 1-2"],
            ["Cell 2-1", "Cell 2-2"],
        ]
    )

    # table with alignment
    doc += Table(
        [["Cell 1", "Cell 2", "Cell 3"]],
        align=["left", "center", "right"],
    )

    # table with header and footer (needs block=True)
    doc += Table(
        [["Cell 1", "Cell 2"]],
        header=["Header 1", "Header 2"],
        footer=["Footer 1", "Footer 2"],
        block=True,
    )

    # table with row and column spanning (needs block=True)
    doc += Table(
        [
            ["Cell 1-1", "Cell 1-2", "Cell 1-3"],
            ["Cell 2-1", "Cell 2-2", "Cell 2-3"],
        ],
        header=[
            [Cell("Column 1", rspan=2), Cell("Columns 2 & 3", cspan=2)],
            ["Column 2", "Column 3"],
        ],
        block=True,
    )

    # table with each cell wrapped in an explicit paragraph if it doesn't
    # already contain block content (needs block=True)
    doc += Table(
        [
            [
                BlockContainer(
                    "This text is implicitly wrapped in a paragraph",
                    BulletList(["Item 1", "Item 2"]),
                ),
                "Cell 2",
                "Cell 3",
            ]
        ],
        align=["left", "center", "right"],
        block=True,
        loose=True,
    )

    # table with character widths
    doc += Table(
        [["Short text", "This is longer text that will be wrapped"]],
        widths=[15, 20],
    )

    # table with percentage widths
    doc += Table(
        [["25% width", "75% width"]],
        widths_pct=[25, 75],
    )

    render_doc(doc, request, powerpack_comparison_files)


@mark.powerpack_compare_file("doc.md")
def test_images(
    request: FixtureRequest, powerpack_comparison_files: ComparisonFiles
):
    from mdforge import BlockImage, Document, InlineImage, Paragraph

    doc = Document()

    # inline image in a paragraph
    doc += Paragraph(
        "Here is an inline image",
        InlineImage("./image.png", alt_text="Inline image"),
        "in a paragraph.",
        auto_space=True,
    )

    # block image with caption and alignment
    doc += BlockImage("./image.png", caption="Block image", align="center")

    render_doc(doc, request, powerpack_comparison_files)


@mark.powerpack_compare_file("doc.md")
def test_html_attributes(
    request: FixtureRequest, powerpack_comparison_files: ComparisonFiles
):

    from mdforge import Attributes, Document, Heading, Ref, Span

    doc = Document()

    # heading with ID, classes, and custom attributes
    my_heading = Heading(
        "Heading with attributes",
        attributes=Attributes(
            html_id="my-heading",
            css_classes=["class1", "class2"],
            attrs={"style": "color: blue;"},
        ),
    )
    doc += my_heading

    # span with attributes
    doc += Span(
        "Text with attributes",
        attributes=Attributes(html_id="my-span", css_classes="class1"),
    )

    # reference to heading by id
    doc += Ref(my_heading, "See previous heading")

    render_doc(doc, request, powerpack_comparison_files)


def test_pandoc_extensions():
    from mdforge import Attributes, Document, Heading, Strikethrough

    doc = Document()

    # requires "header_attributes"
    doc += Heading("Heading 1", attributes=Attributes(html_id="heading-1"))

    # requires "strikeout"
    doc += Strikethrough("This text is struck through")

    # get required pandoc extensions
    extensions = doc.get_pandoc_extensions()
    assert extensions == ["header_attributes", "strikeout"]
