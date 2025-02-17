"""
Inline elements.
"""

from pyrollup import rollup

from . import text
from .text import *  # noqa

__all__ = rollup(text)
