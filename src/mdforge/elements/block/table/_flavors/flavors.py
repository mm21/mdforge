"""
Listing of table flavors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .....element import RenderContext
from .....types import FlavorType
from .._context import BaseRenderContext
from .._params import TableParams
from .._variant import BaseTableVariant, VariantConfig
from .frame.context import FrameRenderContext
from .frame.variants import GRID_VARIANT, MULTILINE_VARIANT


@dataclass(frozen=True, kw_only=True)
class TableFlavorSpec[VariantT: BaseTableVariant]:
    """
    Specification of markdown table flavor.
    """

    variant_config: VariantConfig[VariantT]
    render_context_cls: type[BaseRenderContext[VariantT]]


FLAVOR_MAP: dict[FlavorType, TableFlavorSpec[Any]] = {
    "pandoc": TableFlavorSpec(
        variant_config=VariantConfig(inline=MULTILINE_VARIANT, block=GRID_VARIANT),
        render_context_cls=FrameRenderContext,
    )
}
"""
Mapping of markdown flavor to table config.
"""


def create_render_context(
    context: RenderContext, params: TableParams, block: bool
) -> BaseRenderContext:
    """
    Create a table render context for the given markdown flavor and capabilities.
    """

    flavor = context.flavor
    err = f"Tables for flavor {flavor} with block={block} not currently supported"

    flavor_spec = FLAVOR_MAP.get(flavor)
    assert flavor_spec, err

    variant = (
        flavor_spec.variant_config.block if block else flavor_spec.variant_config.inline
    )
    assert variant, err

    variant.validate_params(params)

    render_context = flavor_spec.render_context_cls(context, params, variant)
    return render_context
