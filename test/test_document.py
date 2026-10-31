import warnings

from pytest import FixtureRequest, mark, raises, warns
from pytest_powerpack import ComparisonFiles

from mdforge import (
    AlignedBlock,
    AlignType,
    Attributes,
    BaseElement,
    BlockContainer,
    BlockImage,
    BulletList,
    Document,
    HorizontalRule,
    InlineContainer,
    InlineImage,
    Paragraph,
    Quote,
    Ref,
    RenderError,
    RenderWarning,
    Section,
    Strong,
    Table,
)

from .conftest import compare_doc, render_doc


@compare_doc
def test_basic(doc: Document):

    section = Section("Basic test")
    doc += section
    section += Paragraph("Hello, world paragraph!")
    section += Paragraph("Hello, world\nmultiline paragraph!")
    section += Paragraph("Hello, world\nmultiline paragraph  \nwith line break!")
    section += "Hello, world text!"
    section += [
        "Hello, world text 2!",
        "Hello, world\nblock text!",
    ]
    section += Strong("Hello, world strong!")


@compare_doc
def test_section(doc: Document):

    sec1 = Section("Section 1")
    sec1 += Paragraph("Hello, world!")

    sec11 = Section("Section 1-1")
    sec11 += BulletList(["a", "b", "c"])
    sec1 += sec11

    sec2 = Section("Section 2")
    sec2 += Paragraph("Hello, world 2!")

    sec3 = Section("Section 3")

    doc += [sec1, sec2, sec3]


@compare_doc
def test_ref(doc: Document):
    """
    Test sections and references to them.
    """

    # section w/attributes
    section_1 = Section(
        "Test section 1",
        attributes=Attributes(
            html_id="section-1",
            css_classes=["class1", "class2"],
            attrs={"style": "color: blue;"},
        ),
    )
    doc += section_1
    section_1 += Ref(section_1)
    section_1 += Ref(section_1, "Link to section 1")

    # section w/implicit id
    section_2 = Section("Test section 2")
    doc += section_2
    section_2 += Ref(section_2)
    section_2 += Ref(section_2, "Link to section 2")

    # section w/formatted title and implicit id
    section_3 = Section(InlineContainer(Strong("Test"), " section 3"))
    doc += section_3
    section_3 += Ref(section_3)

    # section w/id
    section_4 = Section("Test section 4", html_id="section-4")
    doc += section_4
    section_4 += Ref(section_4)

    # refs by id
    refs = Section("Refs by id")
    doc += refs
    refs += Ref("section-4", "Link to section 4 by id")
    refs += Ref("#section-1", "Link to section 1 by id")

    # refs by id w/text looked up from section, including forward ref and ref in
    # table cell
    refs += Ref("section-4")
    refs += Ref("section-5")
    refs += Table([[Ref("section-1")]])

    section_5 = Section("Test section 5", html_id="section-5")
    section_5 += Section("Test section 5-1", html_id="section-5-1")
    section_5 += Ref("section-5-1")
    doc += section_5

    assert doc.get_pandoc_extensions() == [
        "header_attributes",
        "implicit_header_references",
        "multiline_tables",
    ]


@compare_doc
def test_section_in_container(doc: Document):
    """
    Test sections nested in plain block containers.
    """

    sec1 = Section("Section 1")
    sec1 += BlockContainer(
        Section("Section 1-1", elements="Hello, world!"),
        Section("Section 1-2"),
    )

    # container added to section before section is added to document
    container = BlockContainer(Section("Section 2-1-1"))
    sec21 = Section("Section 2-1", elements=container)
    sec2 = Section("Section 2", elements=BlockContainer(sec21))

    doc += [sec1, sec2, BlockContainer(Section("Section 3"))]


@compare_doc
def test_quote(doc: Document):
    """
    Test block quotes.
    """

    doc += Quote("Single line quote")
    doc += Quote(
        Paragraph("Multiple", Strong("paragraph"), "quote", auto_space=True),
        "Second paragraph\nwith multiple lines",
        BulletList(["a", "b"]),
        Quote("Nested quote"),
    )


@compare_doc
def test_aligned_block(doc: Document):
    """
    Test aligned blocks.
    """

    doc += AlignedBlock(
        Paragraph("Centered paragraph"),
        Table([["Cell 1", "Cell 2"]], header=["Header 1", "Header 2"]),
    )
    doc += AlignedBlock("Left-aligned text", align="left")
    doc += AlignedBlock("Right-aligned text", align="right")


@compare_doc
def test_horizontal_rule(doc: Document):
    """
    Test horizontal rules.
    """

    doc += HorizontalRule()
    doc += Paragraph("Between rules")
    doc += HorizontalRule()


@compare_doc
def test_images(doc: Document):
    """
    Test inline and block images.
    """

    doc += Paragraph(
        "Here is an inline image",
        InlineImage("./image.png", alt_text="Inline image"),
        "in the middle of a paragraph.",
        auto_space=True,
    )

    aligns: list[AlignType | None] = [
        "left",
        "center",
        "right",
        "default",
        None,
    ]
    for align in aligns:
        doc += [
            Paragraph(f"Here is a {align}-aligned block image:"),
            BlockImage(
                "./image.png",
                caption=InlineContainer(
                    f"Block image",
                    Strong(str(align)),
                    "aligned",
                    auto_space=True,
                ),
                align=align,
                attributes=Attributes(
                    html_id=f"block-image-{align}", css_classes="block-image"
                ),
            ),
        ]


@mark.powerpack_compare_file("doc.md")
def test_frontmatter(
    request: FixtureRequest, powerpack_comparison_files: ComparisonFiles
):
    doc = Document(frontmatter={"title": "Doc 1"}, elements=Paragraph("Hello, world!"))

    render_doc(doc, request, powerpack_comparison_files)


def test_attributes_copy():

    attributes = Attributes(
        html_id="attrs-1",
        css_classes=["class1", "class2"],
        attrs={"attr1": "value1"},
    )
    attributes_copy = attributes._copy(css_classes="class3", attrs={"attr2": "value2"})

    assert attributes_copy.html_id == "attrs-1"
    assert attributes_copy.css_classes == ["class1", "class2", "class3"]
    assert attributes_copy.attrs == {"attr1": "value1", "attr2": "value2"}


def test_standalone():
    """
    Test rendering elements standalone, outside of a document.
    """

    section = Section("Section 1", html_id="section-1")
    section += Ref("section-1-1")
    section += Section("Section 1-1", html_id="section-1-1")

    assert section.render(flavor="pandoc") == "\n".join(
        [
            "# Section 1 {#section-1}",
            "",
            "[Section 1-1](#section-1-1)",
            "",
            "## Section 1-1 {#section-1-1}",
        ]
    )

    container = BlockContainer(Section("Section 1"), Section("Section 2"))
    assert container.render(flavor="pandoc") == "# Section 1\n\n# Section 2"

    # section without title
    assert Section(elements="Text").render(flavor="pandoc") == "Text"


def test_levels():
    """
    Test inferred and explicit levels.
    """

    def render(element: BaseElement) -> str:
        # fail upon any warnings, e.g. skipped level
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            return element.render(flavor="pandoc")

    # nested section rendered standalone is relative to itself
    inner = Section("Inner", elements=Section("Sub"))
    Document(elements=Section("Outer", elements=inner))
    assert render(inner) == "# Inner\n\n## Sub"

    # explicit level for fragment, propagated to nested sections
    fragment = Section("Fragment", level=3, elements=Section("Sub"))
    assert render(fragment) == "### Fragment\n\n#### Sub"

    # explicit level matching placement, including through untitled section
    doc = Document(
        elements=Section(
            "Section 1",
            elements=Section(elements=Section("Section 1-1-1", level=3)),
        )
    )
    assert render(doc) == "# Section 1\n\n### Section 1-1-1\n"

    # explicit level not nested in containing level
    doc = Document(elements=Section("Section 1", elements=Section("1-1", level=1)))
    with raises(RenderError):
        doc.render(flavor="pandoc")

    # explicit level skipping a level
    doc = Document(elements=Section("Section 1", elements=Section("1-1", level=3)))
    with warns(RenderWarning):
        doc.render(flavor="pandoc")

    # inferred level exceeding maximum
    section = Section("Section", level=6, elements=Section("Sub"))
    with raises(RenderError):
        section.render(flavor="pandoc")
