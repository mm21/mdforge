from __future__ import annotations

from typing import Literal

__all__ = [
    "FlavorType",
    "AlignType",
]

type FlavorType = Literal["pandoc"]
"""
Markdown flavors supported. The following additional flavors are planned:

- `github`
- `myst`
"""

type AlignType = Literal["left", "center", "right", "default"]
"""
Alignments used for various elements.
"""

VALID_ALIGNS = ["left", "center", "right", "default"]
