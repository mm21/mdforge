"""
Table variants: describe table syntax per Markdown flavor.

In general, a given syntax for a given flavor may or may not support block content like
paragraphs, lists, etc. Therefore each flavor must specify which configurations to use
for inline-only vs block-allowed syntaxes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ._params import TableParams

__all__ = [
    "VariantConfig",
    "BaseTableVariant",
]


@dataclass(frozen=True, kw_only=True)
class BaseTableVariant(ABC):
    """
    Base class to encapsulate a table variant.
    """

    name: str
    """
    Name associated with this table variant.
    """

    @abstractmethod
    def validate_params(self, params: TableParams):
        """
        Ensure this variant can be rendered given params.
        """
        ...


@dataclass(frozen=True)
class VariantConfig[VariantT: BaseTableVariant]:
    """
    Encapsulates table configs for a specific Markdown flavor, distinguishing between
    tables supporting block elements vs inline-only.
    """

    inline: VariantT
    block: VariantT | None
