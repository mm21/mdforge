"""
Listing of table flavors.
"""

from __future__ import annotations

from .....types import FlavorType
from .flavor import BaseTableVariant, TableFlavor
from .frame.variants import GRID_VARIANT, MULTILINE_VARIANT

FLAVOR_MAP: dict[FlavorType, TableFlavor] = {
    "pandoc": TableFlavor(inline=MULTILINE_VARIANT, block=GRID_VARIANT),
}
"""
Mapping of flavor names to table configs.
"""


def lookup_variant(flavor: FlavorType, block: bool) -> BaseTableVariant:

    err = (
        f"Tables for flavor {flavor} with block={block} not currently supported"
    )

    table_flavor = FLAVOR_MAP.get(flavor)
    assert table_flavor is not None, err

    variant = table_flavor.block if block else table_flavor.inline
    assert variant is not None, err

    return variant
