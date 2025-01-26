from __future__ import annotations

from typing import Literal

__all__ = [
    "FlavorType",
]

type FlavorType = Literal["pandoc"]
"""
Markdown flavors supported. The following additional flavors are planned:

- `github`
- `myst`
"""
