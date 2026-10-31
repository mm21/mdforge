"""
Encapsulates context for rendering tables.
"""

from abc import ABC, abstractmethod
from typing import Generator

from ....element import RenderContext
from ._params import TableParams
from ._variant import BaseTableVariant


class BaseRenderContext[VariantT: BaseTableVariant](ABC):
    """
    Encapsulates all state needed to render a table: immutable params and variant info.
    """

    context: RenderContext
    """
    Context for rendering the overall document.
    """

    params: TableParams
    variant: VariantT

    def __init__(self, context: RenderContext, params: TableParams, variant: VariantT):
        self.context = context
        self.params = params
        self.variant = variant

    @abstractmethod
    def render(self) -> Generator[str, None, None]:
        """
        Render table.
        """
        ...
