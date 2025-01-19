"""
Listing of table flavors.
"""

from __future__ import annotations

from ....types import FlavorType
from .flavor import BaseTableConfig, TableFlavor
from .frame.configs import GRID_CONFIG, MULTILINE_CONFIG

FLAVOR_MAP: dict[FlavorType, TableFlavor] = {
    "pandoc": TableFlavor(inline=MULTILINE_CONFIG, block=GRID_CONFIG),
}
"""
Mapping of flavor names to table configs.
"""


def lookup_config(flavor: FlavorType, block: bool) -> BaseTableConfig:

    err = (
        f"Tables for flavor {flavor} with block={block} not currently supported"
    )

    table_flavor = FLAVOR_MAP.get(flavor)
    assert table_flavor is not None, err

    config = table_flavor.block if block else table_flavor.inline
    assert config is not None, err

    return config
