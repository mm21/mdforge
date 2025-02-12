from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Generator

from pytest import Item, fail, fixture, mark

if TYPE_CHECKING:
    from pytest_powerpack import ComparisonFiles

from mdforge import Document

pytest_plugins = ["pytest_powerpack"]

logging.basicConfig(level=logging.INFO)


def pytest_collection_modifyitems(items: list[Item]):

    # add marker for each testcase to indicate filename to compare
    for item in items:
        item.add_marker(mark.powerpack_compare_file("doc.md"))


@fixture
def doc(
    powerpack_comparison_files: ComparisonFiles,
) -> Generator[Document, None, None]:
    """
    Create a document, write it, and compare its contents against the expected
    contents.
    """

    import pytest_powerpack

    doc = Document()
    yield doc

    # consider any failures as test failures instead of teardown failures
    try:
        doc.render(powerpack_comparison_files.out_file)
        pytest_powerpack.compare_files(powerpack_comparison_files)
    except AssertionError as e:
        fail(f"Document comparison failed: {e}", pytrace=True)
