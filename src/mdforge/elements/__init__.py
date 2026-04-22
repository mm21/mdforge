"""
Primitive Markdown elements which can be inserted into a document or section.
"""

from pyrollup import rollup

from . import block, inline
from .block import *  # noqa
from .inline import *  # noqa

__all__ = rollup(block, inline)
