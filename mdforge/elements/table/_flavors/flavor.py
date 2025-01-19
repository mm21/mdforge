"""
Table configurations: describe table syntax per Markdown flavor.

In general, a given syntax for a given flavor may or may not support block
content like paragraphs, lists, etc. Therefore each flavor must specify
which configurations to use for inline-only vs block-allowed syntaxes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator

from .._params import TableParams


class BaseTableConfig(ABC):
    """
    Base class to represent configuration for a given table flavor.
    """

    @abstractmethod
    def render(self, params: TableParams) -> Generator[str, None, None]:
        """
        Render this table using the provided params.
        """
        ...


@dataclass
class TableFlavor:
    """
    Encapsulates table configs for a specific flavor, distinguishing between
    tables supporting block elements vs inline-only.
    """

    inline: BaseTableConfig
    block: BaseTableConfig | None
