from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from pytest import FixtureRequest, Parser, fixture, mark

if TYPE_CHECKING:
    from pytest_powerpack import ComparisonFiles

from mdforge import Document

pytest_plugins = ["pytest_powerpack"]

logging.basicConfig(level=logging.INFO)


def pytest_addoption(parser: Parser):
    """
    Add options to additionally invoke pandoc on rendered markdown files.
    """

    parser.addoption(
        "--html",
        action="store_true",
        default=False,
        help="Generate .html from .md outputs",
    )

    parser.addoption(
        "--latex",
        action="store_true",
        default=False,
        help="Generate .latex from .md outputs",
    )

    parser.addoption(
        "--pdf",
        action="store_true",
        default=False,
        help="Generate .pdf from .md outputs",
    )


@fixture
def doc() -> Document:
    """
    Create a document.
    """
    return Document()


def compare_doc(func: Callable):
    """
    Decorator to render this document for pandoc flavor and compare against
    the expected one.

    Could be done in the doc fixture during teardown, but this way the test
    itself can fail rather than teardown.
    """

    @mark.powerpack_compare_file("doc.md")
    def wrapper(
        doc: Document,
        request: FixtureRequest,
        powerpack_comparison_files: ComparisonFiles,
    ):
        # invoke testcase
        func(doc=doc)

        # render and perform document checks
        render_doc(doc, request, powerpack_comparison_files)

    return wrapper


def render_doc(
    doc: Document,
    request: FixtureRequest,
    powerpack_comparison_files: ComparisonFiles,
):
    """
    Render document for pandoc flavor, run pandoc based on command line flags,
    and compare output.
    """
    # just-in-time import so asserts can be rewritten
    import pytest_powerpack

    # render document
    doc.render_file(powerpack_comparison_files.out_file, flavor="pandoc")

    # additionally run pandoc if flags passed
    html = bool(request.config.getoption("--html"))
    latex = bool(request.config.getoption("--latex"))
    pdf = bool(request.config.getoption("--pdf"))

    if any([html, latex, pdf]):
        _run_pandoc(
            doc,
            powerpack_comparison_files.out_file,
            html=html,
            latex=latex,
            pdf=pdf,
        )

    # compare output
    pytest_powerpack.compare_files(powerpack_comparison_files)


def _run_pandoc(
    doc: Document, md_path: Path, *, html: bool, latex: bool, pdf: bool
):
    """
    Run pandoc to generate the given artifacts.
    """

    pandoc_path = md_path.parent / "pandoc"
    pandoc_path.mkdir(parents=True, exist_ok=True)

    md_args = ["markdown"] + doc.get_pandoc_extensions()

    base_cmd = [
        "pandoc",
        str(md_path),
        "-f",
        "+".join(md_args),
    ]

    formats = (
        (["html"] if html else [])
        + (["latex"] if latex else [])
        + (["pdf"] if pdf else [])
    )

    for fmt in formats:
        out_path = pandoc_path / f"{md_path.stem}.{fmt}"
        cmd = base_cmd + ["-t", fmt, "-o", str(out_path)]

        logging.info(f"Running: {' '.join(cmd)}")
        subprocess.check_call(cmd)
