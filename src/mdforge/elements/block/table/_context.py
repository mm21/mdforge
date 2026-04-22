"""
Encapsulates context for rendering tables.
"""

from abc import ABC, abstractmethod
from typing import Generator

from ....types import FlavorType
from ._params import TableParams
from ._variant import BaseTableVariant


class BaseRenderContext[VariantT: BaseTableVariant](ABC):
    """
    Encapsulates all state needed to render a table: immutable params and
    variant info.
    """

    flavor: FlavorType
    params: TableParams
    variant: VariantT

    def __init__(
        self, flavor: FlavorType, params: TableParams, variant: VariantT
    ):
        self.flavor = flavor
        self.params = params
        self.variant = variant

    @abstractmethod
    def render(self) -> Generator[str, None, None]:
        """
        Render table.
        """
        ...
