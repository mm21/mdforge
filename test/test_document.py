from pytest import mark

from mdforge import (
    Attributes,
    BulletList,
    Document,
    Heading,
    Paragraph,
    Ref,
    Section,
)

from .conftest import unused


def test_basic(doc: Document):

    doc += Heading("Basic test")
    doc += Paragraph("Hello, world!")
    doc += "Hello, world 2!"
    doc += [
        "Hello, world\n3!",
        "Hello, world 4!",
    ]


def test_section(doc: Document):

    sec1 = Section(heading="Section 1")
    sec1 += Paragraph("Hello, world!")

    sec11 = Section(heading="Section 1-1")
    sec11 += BulletList(["a", "b", "c"])
    sec1 += sec11

    sec2 = Section(heading="Section 2")
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
            html_attrs={"style": "color: blue;"},
            css_classes=["class1", "class2"],
        ),
    )
    doc += heading_1
    doc += Paragraph(Ref(heading_1))
    doc += Paragraph(Ref(heading_1, "Link to heading 1"))

    # heading w/implicit id
    heading_2 = Heading("Test heading 2")
    doc += heading_2
    doc += Paragraph(Ref(heading_2))
    doc += Paragraph(Ref(heading_2, "Link to heading 2"))

    # section
    section_1 = Section(heading="Test section 1")
    doc += section_1
    doc += Paragraph(Ref(section_1))
    doc += Paragraph(Ref(section_1, "Link to section 1"))


@mark.frontmatter({"title": "Doc 1"})
@mark.elements([(Paragraph, ("Hello, world!",), {})])
def test_frontmatter(doc: Document):
    unused(doc)
