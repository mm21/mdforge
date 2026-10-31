"""
Test validation of inputs.

Thanks to [Claude](https://claude.ai/) for assisting with these tests.
"""

from typing import Any

from pytest import raises

from mdforge import (
    Attributes,
    BlockContainer,
    BlockImage,
    BulletList,
    Cell,
    DefinitionItem,
    DefinitionList,
    Document,
    InlineContainer,
    ListItem,
    Paragraph,
    Ref,
    RenderError,
    Section,
    Table,
    Text,
    ValidationError,
)
from mdforge._norm import CoerceSpec, norm_obj


def test_text_elements():

    with raises(ValidationError):
        Text("This text\nhas multiple lines")

    with raises(ValidationError):
        Paragraph("This paragraph has\n\na blank line")

    # ref to a section without a title
    with raises(ValidationError):
        Ref(Section())


def test_block_elements():

    with raises(ValidationError):
        BlockImage("./image.png", align="invalid")  # type: ignore[arg-type]

    # create a definition item with a block element
    def_item = DefinitionItem("Term", BulletList(["Item 1", "Item 2"]))

    # try to use it in a compact definition list
    # (only allows inline elements)
    with raises(ValidationError):
        DefinitionList([def_item], compact=True)


def test_tables():

    # non-int width provided
    with raises(ValidationError):
        Table(
            [["Cell 1", "Cell 2", "Cell 3"]],
            widths=[10, 10, None],  # type: ignore[list-item]
        )

    # both widths and widths_pct being provided
    with raises(ValidationError):
        Table(
            [["Cell 1", "Cell 2", "Cell 3"]],
            widths=[10, 10, 10],
            widths_pct=[30, 30, 40],
        )

    # width_pct not adding up to 100
    with raises(ValidationError):
        Table(
            [["Cell 1", "Cell 2", "Cell 3"]],
            widths_pct=[30, 30, 30],
        )

    # zero width_pct
    with raises(ValidationError):
        Table(
            [["Cell 1", "Cell 2", "Cell 3"]],
            widths_pct=[0, 50, 50],
        )

    # widths length mismatch
    with raises(ValidationError):
        Table(
            [["Cell 1", "Cell 2", "Cell 3"]],
            widths=[10, 20],  # only 2 widths for 3 columns
        )

    # widths_pct length mismatch
    with raises(ValidationError):
        Table(
            [["Cell 1", "Cell 2", "Cell 3"]],
            widths_pct=[50, 50],  # only 2 percentages for 3 columns
        )

    # invalid row specification (empty)
    with raises(ValidationError):
        Table([])

    # invalid row type
    with raises(ValidationError):
        Table([1, 2, 3])  # type: ignore[list-item] # integers are not valid cell types

    # merged cells with inconsistent column counts
    with raises(ValidationError):
        Table(
            [
                ["Cell 1", "Cell 2", "Cell 3"],
                ["Cell 1", Cell("Spans 2 columns", cspan=2)],
                ["Cell 1", "Cell 2", "Cell 3", "Extra Cell"],
            ]
        )

    # block element in an inline table
    block_element = BulletList(["Item 1", "Item 2"])
    with raises(ValidationError):
        Table(
            [[block_element, "Cell 2"]],
            block=False,  # specify inline-only table
        )

    # table with loose=True but block=False
    with raises(ValidationError):
        Table([["Cell 1", "Cell 2"]], loose=True)

    # table with a very long word and a small width
    very_long_word = "ThisIsAnExtremelyLongWordThatCannotBeWrappedProperly"
    with raises(RenderError):
        table = Table(
            [[very_long_word]],
            widths=[10],  # too small for the long word
        )
        table.render(flavor="pandoc")

    # multiline table with footer
    with raises(RenderError):
        table = Table([["Cell 1", "Cell 2"]], footer=["Footer 1", "Footer 2"])
        table.render(flavor="pandoc")


def test_containers():

    block_element = BulletList(["Item 1", "Item 2"])

    # inline container with block content
    with raises(ValueError):
        InlineContainer("Text", block_element)  # type: ignore[arg-type]


def test_normalize():

    # normalize to an incompatible type
    with raises(ValueError):
        norm_obj(123, str)

    # coercion that fails
    def bad_coercion(obj: int) -> Any:
        return None

    with raises(ValueError):
        norm_obj(123, str, CoerceSpec(bad_coercion, int))


def test_ids():

    # conflicting ids
    with raises(ValidationError):
        Section("Section", html_id="id-1", attributes=Attributes(html_id="id-2"))

    # invalid levels
    for level in [0, 7]:
        with raises(ValidationError):
            Section("Section", level=level)

    # id and attributes require title
    with raises(ValidationError):
        Section(html_id="id-1")
    with raises(ValidationError):
        Section(attributes=Attributes(css_classes="class1"))


def test_ref_by_id():

    # ref by id not found
    doc = Document(elements=Ref("id-1"))
    with raises(RenderError):
        doc.render(flavor="pandoc")

    # ref by id w/duplicate ids
    doc = Document(
        elements=[
            Ref("id-1"),
            Section("Section 1", html_id="id-1"),
            Section("Section 2", html_id="id-1"),
        ]
    )
    with raises(RenderError):
        doc.render(flavor="pandoc")

    # ref by id rendered standalone
    with raises(RenderError):
        Ref("id-1").render(flavor="pandoc")

    # ref by id to section outside of section rendered standalone
    section = Section("Section", elements=Ref("id-1"))
    Document(elements=[Section("Section 1", html_id="id-1"), section])
    with raises(RenderError):
        section.render(flavor="pandoc")

    # ref by id w/text doesn't require lookup
    assert Ref("id-1", "Text").render(flavor="pandoc") == "[Text](#id-1)"


def test_sections_disallowed():

    section = Section("Section")
    nested_section = BlockContainer(Paragraph("Text"), Section("Section"))

    for element in [section, nested_section]:
        with raises(ValidationError):
            ListItem(element)
        with raises(ValidationError):
            BulletList([element])
        with raises(ValidationError):
            BulletList([ListItem("Item", [element])])
        with raises(ValidationError):
            DefinitionItem("Term", element)
        with raises(ValidationError):
            Cell(element)
        with raises(ValidationError):
            Table([[element]], block=True)

    # section added to container after container is placed in a cell
    container = BlockContainer(Paragraph("Text"))
    Table([[container]], block=True)
    with raises(ValidationError):
        container += Section("Section")

    # section added to container nested in a list item
    container = BlockContainer(Paragraph("Text"))
    BulletList([ListItem("Item", [BlockContainer(container)])])
    with raises(ValidationError):
        container += Section("Section")


def test_placement():

    # element can only be placed once
    paragraph = Paragraph("Text")
    Document(elements=paragraph)
    with raises(ValidationError):
        Document(elements=paragraph)

    text = Text("Text")
    Paragraph(text)
    with raises(ValidationError):
        Cell(text)
