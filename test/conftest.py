from pathlib import Path
import logging

from pytest import FixtureRequest, Mark, fixture

pytest_plugins = ["pytest_powerpack"]

logging.basicConfig(level=logging.INFO)

DOCUMENTS_PATH = Path("test/documents")


@fixture
def document_text(request: FixtureRequest) -> str:

    # get filename
    marker: Mark = request.node.get_closest_marker("filename")
    assert isinstance(marker, Mark)
    assert len(marker.args) == 1
    filename = marker.args[0]
    assert isinstance(filename, str)

    path = DOCUMENTS_PATH / filename

    with path.open() as fh:
        return fh.read()
