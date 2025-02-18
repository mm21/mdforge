from pytest import mark

from mdforge import BulletList, Document, Heading, Paragraph, Section

from .conftest import unused


def test_basic(doc: Document):

    doc += Heading("Basic test")
    doc += Paragraph("Hello, world!")

    # TODO:
    # - add block content
    # - move lists to separate test


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


@mark.frontmatter({"title": "Doc 1"})
@mark.elements([(Paragraph, ("Hello, world!",), {})])
def test_frontmatter(doc: Document):
    unused(doc)
