"""
Primitive Markdown elements which can be inserted into a document or section.
"""

from pyrollup import rollup

from . import basic, page, table
from .basic import *  # noqa
from .table import *  # noqa

__all__ = rollup(basic, page, table)
