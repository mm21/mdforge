from typing import cast

from mdforge import (
    BaseItemList,
    BlockContainer,
    BulletList,
    DefinitionItem,
    DefinitionList,
    Document,
    Emph,
    ListItem,
    NumberedList,
    Paragraph,
    Section,
    Strong,
)

from .conftest import compare_doc

LIST_CLASSES = cast(list[type[BaseItemList]], [BulletList, NumberedList])
LIST_NAMES = [cls.__name__ for cls in LIST_CLASSES]


@compare_doc
def test_flat(doc: Document):
    """
    Test lists with no nesting.
    """

    for list_cls, name in zip(LIST_CLASSES, LIST_NAMES):

        section = Section(name)
        doc += section
        section += list_cls(
            [
                "a",
                "b",
                "c",
            ]
        )


@compare_doc
def test_nested(doc: Document):
    """
    Test lists with nesting.
    """

    for list_cls, name, idx in zip(LIST_CLASSES, LIST_NAMES, range(len(LIST_CLASSES))):

        other_list_cls = LIST_CLASSES[idx - 1]
        other_list_name = other_list_cls.__name__

        section = Section(name)
        doc += section
        section += list_cls(
            [
                "a",
                ListItem(
                    "b",
                    [
                        "b1",
                        "b2",
                        "b3",
                    ],
                ),
                ListItem(
                    "c",
                    [
                        "c1",
                        "c2",
                        ListItem(
                            "c3",
                            [
                                "c3-1",
                                "c3-2",
                                "c3-3",
                            ],
                        ),
                    ],
                ),
                ListItem(
                    f"d ({other_list_name})",
                    other_list_cls(
                        [
                            "d1",
                            "d2",
                            ListItem(
                                "d3",
                                [
                                    "d3-1",
                                    "d3-2",
                                    "d3-3",
                                ],
                            ),
                        ]
                    ),
                ),
            ]
        )


@compare_doc
def test_tight(doc: Document):
    """
    Test "tight" pandoc lists.
    """

    for list_cls, name in zip(LIST_CLASSES, LIST_NAMES):
        section = Section(f"{name}, 1 element")
        doc += section
        section += list_cls(["a"])

        section = Section(f"{name}, 3 elements")
        doc += section
        section += list_cls(["a", "b", "c"])

        section = Section(f"{name}, 3 elements w/nesting")
        doc += section
        section += list_cls(
            [
                ListItem("a", ["a1", "a2", "a3"]),
                ListItem("b", ["b1", "b2", "b3"]),
                ListItem("c", ["c1", "c2", "c3"]),
            ]
        )


@compare_doc
def test_loose(doc: Document):
    """
    Test "loose" pandoc lists.
    """

    for list_cls, name in zip(LIST_CLASSES, LIST_NAMES):

        section = Section(f"{name}, 1 element")
        doc += section
        section += list_cls(["a"], loose=True)

        section = Section(f"{name}, 1 element (w/paragraph)")
        doc += section
        section += list_cls(["a\n\nb"], loose=True)

        section = Section(f"{name}, implicit loose (paragraphs)")
        doc += section
        section += list_cls(
            [
                "a",
                BlockContainer(
                    Paragraph("b (paragraph 1)"), Paragraph("b (paragraph 2)")
                ),
            ],
        )

        section = Section(f"{name}, implicit loose (paragraph, list)")
        doc += section
        section += list_cls(
            [
                "a",
                BlockContainer(
                    Paragraph("b (paragraph)"), list_cls(["b1", "b2", "b3"])
                ),
            ],
        )

        section = Section(f"{name}, implicit loose (nested list)")
        doc += section
        section += list_cls(
            [
                "a",
                list_cls(["b1", "b2", "b3"]),
            ],
        )

        section = Section(f"{name}, 4 elements")
        doc += section
        section += list_cls(
            [
                "a",
                "b",
                ListItem("c (not loose)", list_cls(["c1", "c2", "c3"])),
                ListItem("d (loose)", list_cls(["d1", "d2", "d3"], loose=True)),
            ],
            loose=True,
        )


@compare_doc
def test_elements(doc: Document):
    """
    Test lists with elements as text.
    """

    for list_cls, name in zip(LIST_CLASSES, LIST_NAMES):

        section = Section(f"{name}, inline")
        doc += section
        section += list_cls(
            [
                Strong("a (strong)"),
                ListItem(
                    Emph("b (emph)"),
                    [
                        "b1",
                        "b2",
                        "b3",
                    ],
                ),
                Strong(Emph("c (strong + emph)")),
            ]
        )

        section = Section(f"{name}, block")
        doc += section
        section += list_cls(
            [
                Strong("a (strong)"),
                ListItem(
                    Emph("b (emph)"),
                    [
                        "b1",
                        "b2",
                        "b3",
                    ],
                ),
                BlockContainer(
                    Paragraph("c (paragraph 1)"), Paragraph("c (paragraph 2)")
                ),
            ]
        )

        section = Section(f"{name}, block (inferred)")
        doc += section
        section += list_cls(
            [
                "a",
                ListItem(
                    "b",
                    [
                        "b1",
                        "b2",
                        "b3",
                    ],
                ),
                "c (paragraph 1)\n\nc (paragraph 2)",
            ]
        )


@compare_doc
def test_definition(doc: Document):

    def inline_items() -> list[DefinitionItem]:
        return [
            DefinitionItem("Term A", "Definition A"),
            DefinitionItem(Strong("Term B (strong)"), Strong("Definition B (strong)")),
            DefinitionItem(
                "Term C", ["Definition C1", Strong("Definition C2 (strong)")]
            ),
        ]

    # inline items (compact or non-compact)
    for compact in [False, True]:
        doc += Section(
            f"Definition list w/inline items, compact={compact}",
            elements=DefinitionList(inline_items(), compact=compact),
        )

    block_items = [
        DefinitionItem(
            "Term A",
            BlockContainer(
                "This is a paragraph.",
                BulletList(["Definition A1", "Definition A2"]),
            ),
        ),
        DefinitionItem("Term B", BulletList(["Definition B1", "Definition B2"])),
        DefinitionItem("Term C", "Definition C"),
    ]

    # block items (non-compact only)
    doc += Section(
        "Definition list w/block items", elements=DefinitionList(block_items)
    )

    assert doc.get_pandoc_extensions() == ["definition_lists"]
