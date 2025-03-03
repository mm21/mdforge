"""
Test validation of inputs.

Thanks to [Claude](https://claude.ai/) for assisting with these tests.
"""

from pytest import raises

from mdforge import (
    BlockImage,
    BulletList,
    Cell,
    DefinitionItem,
    DefinitionList,
    InlineContainer,
    Paragraph,
    RenderError,
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


def test_block_elements():

    with raises(ValidationError):
        BlockImage("./image.png", align="invalid")

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
            [["Cell1", "Cell2", "Cell3"]],
            widths=[10, 10, None],
        )

    # both widths and widths_pct being provided
    with raises(ValidationError):
        Table(
            [["Cell1", "Cell2", "Cell3"]],
            widths=[10, 10, 10],
            widths_pct=[30, 30, 40],
        )

    # width_pct not adding up to 100
    with raises(ValidationError):
        Table(
            [["Cell1", "Cell2", "Cell3"]],
            widths_pct=[30, 30, 30],
        )

    # zero width_pct
    with raises(ValidationError):
        Table(
            [["Cell1", "Cell2", "Cell3"]],
            widths_pct=[0, 50, 50],
        )

    # widths length mismatch
    with raises(ValidationError):
        Table(
            [["Cell1", "Cell2", "Cell3"]],
            widths=[10, 20],  # only 2 widths for 3 columns
        )

    # widths_pct length mismatch
    with raises(ValidationError):
        Table(
            [["Cell1", "Cell2", "Cell3"]],
            widths_pct=[50, 50],  # only 2 percentages for 3 columns
        )

    # invalid row specification (empty)
    with raises(ValidationError):
        Table([])

    # invalid row type
    with raises(ValidationError):
        Table([1, 2, 3])  # Integers are not valid cell types

    # merged cells with inconsistent column counts
    with raises(ValidationError):
        Table(
            [
                ["Cell1", "Cell2", "Cell3"],
                ["Cell1", Cell("Spans 2 columns", cspan=2)],
                ["Cell1", "Cell2", "Cell3", "Extra Cell"],
            ]
        )

    # create a block element and try to put it in an inline table
    block_element = BulletList(["Item 1", "Item 2"])

    with raises(ValidationError):
        Table(
            [[block_element, "Cell2"]],
            block=False,  # Specify inline-only table
        )

    # table with a very long word and a small width
    very_long_word = "ThisIsAnExtremelyLongWordThatCannotBeWrappedProperly"

    with raises(RenderError):
        table = Table(
            [[very_long_word]],
            widths=[10],  # Too small for the long word
        )
        # force rendering to trigger the wrap error
        list(table._render_block("pandoc"))


def test_containers():

    block_element = BulletList(["Item 1", "Item 2"])

    # inline container with block content
    with raises(ValueError):
        InlineContainer("Text", block_element)


def test_normalize():

    # normalize to an incompatible type
    with raises(ValueError):
        norm_obj(123, str)

    # coercion that fails
    def bad_coercion(obj):
        return None

    with raises(ValueError):
        norm_obj(123, str, CoerceSpec(bad_coercion, int))
