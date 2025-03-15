# MDForge
Pythonic multi-flavor Markdown generator

[![Python versions](https://img.shields.io/pypi/pyversions/mdforge.svg)](https://pypi.org/project/mdforge)
[![PyPI](https://img.shields.io/pypi/v/mdforge?color=%2334D058&label=pypi%20package)](https://pypi.org/project/mdforge)
[![Tests](./badges/tests.svg?dummy=8484744)]()
[![Coverage](./badges/cov.svg?dummy=8484744)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

- [MDForge](#mdforge)
  - [Motivation](#motivation)
  - [Getting started](#getting-started)
  - [Working with documents](#working-with-documents)
  - [Pythonic Markdown elements](#pythonic-markdown-elements)
    - [Formatting](#formatting)
    - [Lists](#lists)
    - [Tables](#tables)
    - [Images](#images)
    - [Rendering standalone elements](#rendering-standalone-elements)
  - [Advanced features](#advanced-features)
    - [HTML attributes](#html-attributes)
    - [Pandoc extensions](#pandoc-extensions)

## Motivation

MDForge provides a Pythonic interface for generating Markdown documents programmatically. It allows you to construct a document tree and render it for various Markdown flavors, making it ideal for applications such as documentation generators and report builders. It emphasizes clean flavor-agnostic elements and type safety.

While MDForge supports the rich capabilities of [Pandoc's Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown), it is designed to support generating documents with multiple flavors from the same document model. Other flavors currently planned are:

- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [MyST Markdown](https://mystmd.org/guide)

## Getting started

First, install using pip:

```bash
pip install mdforge
```

Create your first Markdown document:

```python
from mdforge import Document, Heading, Paragraph, Strong
from pathlib import Path

# create a document
doc = Document()

# add elements
doc += [
    Heading("My first MDForge document"),
    Paragraph("Hello, ", Strong("world"), "!"),
]

# render pandoc-flavored Markdown document to a file
doc.render_file("doc.md", flavor="pandoc")
```

This is rendered as:

```markdown
# My first MDForge document

Hello, **world**!

```

## Working with documents

The `Document` class is the fundamental interface to create a Markdown document. It implements a [Composite pattern](https://en.wikipedia.org/wiki/Composite_pattern) wherein elements are composed using the `+=` operator:

```python
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

# add sections to document
doc += [intro, key_points]

doc.render_file("doc.md", flavor="pandoc")
```

This is rendered as:

```markdown
---
title: My Document
author: Me
---

# Introduction

This is an introduction paragraph.

# Key Points

- Point 1
- Point 2
- Point 3
<!-- end of list -->

## Point 1

Elaboration on point 1:

- Point 1-a
- Point 1-b
<!-- end of list -->

## Point 2

Elaboration on point 2.

## Point 3

Elaboration on point 3.

```

Note the following observations:

- Sections can be nested in other sections, with optional headings
- Heading levels for sections are automatically set by their placement in the hierarchy
- Strings added to a document or section via `+=` are treated as raw text
- A comment is placed at the end of each list; this disambiguates the end of one list and the start of the next, in case there are no other elements in between

## Pythonic Markdown elements

MDForge provides a set of Markdown elements that can be composed to create rich documents. Not all common elements are implemented yet, e.g. code blocks. Nonetheless, you can insert raw text (which may be pre-formatted as Markdown) using `+=`.

We have already seen basic elements and container elements. The following examples illustrate the use of other common elements.

### Formatting

```python
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

doc.render_file("doc.md", flavor="pandoc")
```

This is rendered as:

```markdown
**Bold text**

_Italicized text_

~~Strikethrough text~~

[Underlined text]{.underline}

**_Bold and italicized text_**

Normal text with **bold** and _italic_ segments.

```

Note the following observations:

- Here we pass `auto_space=True` in `Paragraph()`; this will automatically insert spaces between the inline elements passed to it
- As underline is not supported in CommonMark, pandoc implements its own [underline syntax](https://pandoc.org/MANUAL.html#underline)

### Lists

MDForge supports bullet lists, numbered lists, and definition lists:

```python
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

doc.render_file("doc.md", flavor="pandoc")
```

This is rendered as:

```markdown
- Item 1
- Item 2
- Item 3
<!-- end of list -->

1. First
1. Second
1. Third
<!-- end of list -->

Term A
:   Definition A

Term B
:   Definition B1
:   Definition B2

<!-- end of definition list -->

- Item 1
- Item 2
  - Item 2-1
  - Item 2-2
  <!-- end of list -->
<!-- end of list -->

- Item 1
- Item 2
  1. Item 2-1
  1. Item 2-2
  <!-- end of list -->
<!-- end of list -->

```

Note the following observations:

- Here we pass `compact=True` in `DefinitionList()`; this will generate [compact definition lists](https://pandoc.org/MANUAL.html#extension-compact_definition_lists) for pandoc flavor
- As mentioned above, a comment disambiguates the end of one list and the start of the next

### Tables

MDForge provides powerful table support with cell spanning, alignment, and formatting:

```python
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

doc.render_file("doc.md", flavor="pandoc")
```

This is rendered as:

```markdown
<!-- table start -->

---------- ----------
Cell 1-1   Cell 1-2  

Cell 2-1   Cell 2-2  
---------------------

<!-- table end -->

<!-- table start: align=['left', 'center', 'right'] -->

-------- -------- --------
Cell 1    Cell 2    Cell 3

--------------------------

<!-- table end -->

<!-- table start: block=True -->

+----------+----------+
| Header 1 | Header 2 |
+==========+==========+
| Cell 1   | Cell 2   |
+==========+==========+
| Footer 1 | Footer 2 |
+==========+==========+

<!-- table end -->

<!-- table start: block=True -->

+----------+---------------------+
| Column 1 | Columns 2 & 3       |
|          +----------+----------+
|          | Column 2 | Column 3 |
+==========+==========+==========+
| Cell 1-1 | Cell 1-2 | Cell 1-3 |
+----------+----------+----------+
| Cell 2-1 | Cell 2-2 | Cell 2-3 |
+----------+----------+----------+

<!-- table end -->

<!-- table start: align=['left', 'center', 'right'], block=True, loose=True -->

+:-----------------------------------------------+:-------------:+--------------:+
| This text is implicitly wrapped in a paragraph | <p>Cell 2</p> | <p>Cell 3</p> |
|                                                |               |               |
| - Item 1                                       |               |               |
| - Item 2                                       |               |               |
| <!-- end of list -->                           |               |               |
+------------------------------------------------+---------------+---------------+

<!-- table end -->

<!-- table start: widths=[15, 20] -->

----------------- ----------------------
Short text        This is longer text   
                  that will be wrapped  

----------------------------------------

<!-- table end -->

<!-- table start: widths_pct=[25, 75] -->

----------- -----------------------------
25% width   75% width                    

-----------------------------------------

<!-- table end -->

```

Note the following observations:

- Merged cells and footers are only supported with `block=True`; this causes pandoc flavor to use a [grid table](https://pandoc.org/MANUAL.html#extension-grid_tables) instead of a [multiline table](https://pandoc.org/MANUAL.html#extension-multiline_tables)
- Pass `loose=True` to ensure all cells are wrapped in a paragraph, even if they don't get parsed as block content (requires `block=True`)
    - This ensures consistently-padded cells
- Use `BlockContainer` to wrap multiple block elements in a single element

### Images

MDForge supports both inline and block images:

```python
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

doc.render_file("doc.md", flavor="pandoc")
```

This is rendered as:

```markdown
Here is an inline image ![Inline image](./image.png) in a paragraph.

![Block image](./image.png){fig-align="center"}

```

Note the following observations:

- Support for caption and alignment depends on flavor

### Rendering standalone elements

Any element class can be rendered by itself, even if not placed in a document. This is useful for generating document snippets which may be embedded in a document, e.g. via a templating engine.

```python
from mdforge import InlineContainer, Strong

element = InlineContainer("This is a ", Strong("test element"))

assert element.render(flavor="pandoc") == "This is a **test element**"
```

## Advanced features

### HTML attributes

For pandoc flavor, HTML attributes can be added to various elements:

```python
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

doc.render_file("doc.md", flavor="pandoc")
```

This is rendered as:

```markdown
# Heading with attributes {#my-heading .class1 .class2 style="color: blue;"}

[Text with attributes]{#my-span .class1}

[See previous heading](#my-heading)

```

### Pandoc extensions

As MDForge is designed with pandoc compatibility in mind, it automatically tracks required pandoc extensions:

```python
from mdforge import Attributes, Document, Heading, Strikethrough

doc = Document()

# requires "header_attributes"
doc += Heading("Heading 1", attributes=Attributes(html_id="heading-1"))

# requires "strikeout"
doc += Strikethrough("This text is struck through")

# get required pandoc extensions
extensions = doc.get_pandoc_extensions()
assert extensions == ["header_attributes", "strikeout"]
```
