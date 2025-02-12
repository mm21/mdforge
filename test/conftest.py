from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Generator, cast

from pytest import Config, FixtureRequest, Item, fail, fixture, mark

if TYPE_CHECKING:
    from pytest_powerpack import ComparisonFiles

from mdforge import BaseElement, Document

pytest_plugins = ["pytest_powerpack"]

logging.basicConfig(level=logging.INFO)


def pytest_configure(config: Config):
    config.addinivalue_line(
        "markers",
        "frontmatter: Pass frontmatter to Document constructor",
    )

    config.addinivalue_line(
        "markers",
        "elements: Pass elements to Document constructor",
    )


def pytest_collection_modifyitems(items: list[Item]):

    # add marker for each testcase to indicate filename to compare
    for item in items:
        item.add_marker(mark.powerpack_compare_file("doc.md"))


@fixture
def doc(
    request: FixtureRequest,
    powerpack_comparison_files: ComparisonFiles,
) -> Generator[Document, None, None]:
    """
    Create a document, write it, and compare its contents against the expected
    contents.
    """

    import pytest_powerpack

    frontmatter_marker = request.node.get_closest_marker("frontmatter")
    elements_marker = request.node.get_closest_marker("elements")

    elements: list[BaseElement] | None = None
    frontmatter: dict[str, Any] | None = None

    if frontmatter_marker:
        assert len(frontmatter_marker.args) == 1

        frontmatter = cast(dict[str, Any], frontmatter_marker.args[0])
        assert isinstance(frontmatter, dict)

    if elements_marker:
        assert len(elements_marker.args)

        elements_arg = cast(
            list[tuple[type[BaseElement], tuple[Any, ...], dict[str, Any]]],
            elements_marker.args[0],
        )

        # instantiate each element with provided args and kwargs
        elements = []
        for element_cls, args, kwargs in elements_arg:
            elements.append(element_cls(*args, **kwargs))

    doc = Document(frontmatter=frontmatter, elements=elements)
    yield doc

    # consider any failures as test failures instead of teardown failures
    try:
        doc.render(powerpack_comparison_files.out_file)
        pytest_powerpack.compare_files(powerpack_comparison_files)
    except AssertionError as e:
        fail(f"Document comparison failed: {e}", pytrace=True)
