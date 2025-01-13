"""
Primitive Markdown elements which can be inserted into a document or section.
"""

from pyrollup import rollup

from . import basic, page, section
from .basic import *  # noqa
from .section import *  # noqa
from .table import table
from .table.table import *  # noqa

__all__ = rollup(basic, page, table, section)
