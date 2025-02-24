"""
Inline elements.
"""

from pyrollup import rollup

from . import basic, text
from .basic import *  # noqa
from .text import *  # noqa

__all__ = rollup(text, basic)
