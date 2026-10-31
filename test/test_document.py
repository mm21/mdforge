from pytest import FixtureRequest, mark
from pytest_powerpack import ComparisonFiles

from mdforge import (
    AlignType,
    Attributes,
    BlockContainer,
    BlockImage,
    BulletList,
    Document,
    InlineContainer,
    InlineImage,
    Paragraph,
    Ref,
    Section,
    Strong,
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

    assert doc.get_pandoc_extensions() == [
        "header_attributes",
        "implicit_header_references",
    ]


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
