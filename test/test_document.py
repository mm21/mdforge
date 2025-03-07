from pytest_powerpack import ComparisonFiles, compare_files

from mdforge import (
    AlignType,
    Attributes,
    BlockImage,
    BulletList,
    Document,
    Heading,
    InlineContainer,
    InlineImage,
    Paragraph,
    Ref,
    Section,
    Strong,
)


def test_basic(doc: Document):

    doc += Heading("Basic test")
    doc += Paragraph("Hello, world paragraph!")
    doc += Paragraph("Hello, world\nmultiline paragraph!")
    doc += Paragraph("Hello, world\nmultiline paragraph  \nwith line break!")
    doc += "Hello, world text!"
    doc += [
        "Hello, world text 2!",
        "Hello, world\nblock text!",
    ]
    doc += Strong("Hello, world strong!")


def test_section(doc: Document):

    sec1 = Section("Section 1")
    sec1 += Paragraph("Hello, world!")

    sec11 = Section("Section 1-1")
    sec11 += BulletList(["a", "b", "c"])
    sec1 += sec11

    sec2 = Section("Section 2")
    sec2 += Paragraph("Hello, world 2!")

    h3 = Heading("Heading 3")

    doc += [sec1, sec2, h3]


def test_ref(doc: Document):
    """
    Test headings and references to them.
    """

    # heading w/attributes
    heading_1 = Heading(
        "Test heading 1",
        attributes=Attributes(
            html_id="heading-1",
            attrs={"style": "color: blue;"},
            css_classes=["class1", "class2"],
        ),
    )
    doc += heading_1
    doc += Ref(heading_1)
    doc += Ref(heading_1, "Link to heading 1")

    # heading w/implicit id
    heading_2 = Heading("Test heading 2")
    doc += heading_2
    doc += Ref(heading_2)
    doc += Ref(heading_2, "Link to heading 2")

    # section
    section_1 = Section(heading="Test section 1")
    doc += section_1
    doc += Ref(section_1)
    doc += Ref(section_1, "Link to section 1")

    assert doc.get_pandoc_extensions() == [
        "header_attributes",
        "implicit_header_references",
    ]


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


def test_frontmatter(powerpack_comparison_files: ComparisonFiles):
    doc = Document(
        frontmatter={"title": "Doc 1"}, elements=Paragraph("Hello, world!")
    )

    doc.render(powerpack_comparison_files.out_file, flavor="pandoc")
    compare_files(powerpack_comparison_files)
