"""
Listings of flavors and syntaxes.
"""

from __future__ import annotations

from .....types import FlavorType
from .flavor import SectionConfig, Separator, TableConfig, TableFlavor

FLAVOR_MAP: dict[FlavorType, TableFlavor] = {
    "pandoc": TableFlavor(
        inline=TableConfig(
            header=SectionConfig(
                Separator(), lower_sep=Separator(inner_corner=" ")
            ),
            content=SectionConfig(
                Separator(line=None),
                lower_sep=Separator(),
                upper_sep=Separator(inner_corner=" "),
            ),
            footer=SectionConfig(Separator()),
            align_space=True,
        ),
        block=TableConfig(
            header=SectionConfig(
                Separator(corner="+"), lower_sep=Separator(line="=", corner="+")
            ),
            content=SectionConfig(Separator(corner="+")),
            footer=SectionConfig(
                Separator(corner="+"),
                lower_sep=Separator(line="=", corner="+"),
                upper_sep=Separator(line="=", corner="+"),
            ),
            cell_sep="|",
            align_char=":",
        ),
    )
}
"""
Mapping of flavors to table configs.

Pandoc inline tables:

```
-------------------------------------------------------------
 Centered   Default           Right Left
  Header    Aligned         Aligned Aligned
----------- ------- --------------- -------------------------
   First    row                12.0 Example of a row that
                                    spans multiple lines.

  Second    row                 5.0 Here's another one. Note
                                    the blank line between
                                    rows.
-------------------------------------------------------------

----------- ------- --------------- -------------------------
   First    row                12.0 Example of a row that
                                    spans multiple lines.

  Second    row                 5.0 Here's another one. Note
                                    the blank line between
                                    rows.
-------------------------------------------------------------
```

Pandoc block tables:

```
+---------------------+-----------------------+
| Location            | Temperature 1961-1990 |
|                     | in degree Celsius     |
|                     +-------+-------+-------+
|                     | min   | mean  | max   |
+=====================+=======+=======+=======+
| Antarctica          | -89.2 | N/A   | 19.8  |
+---------------------+-------+-------+-------+
| Earth               | -89.2 | 14    | 56.7  |
+=====================+=======+=======+=======+
| Average             | -89.2 | N/A   | 38.25 |
+=====================+=======+=======+=======+

+---------------+---------------+--------------------+
| Right         | Left          | Centered           |
+==============:+:==============+:==================:+
| Bananas       | $1.34         | built-in wrapper   |
+---------------+---------------+--------------------+

+--------------:+:--------------+:------------------:+
| Right         | Left          | Centered           |
+---------------+---------------+--------------------+
```
"""


def lookup_config(flavor: FlavorType, block: bool) -> TableConfig:

    err = (
        f"Tables for flavor {flavor} with block={block} not currently supported"
    )

    table_flavor = FLAVOR_MAP.get(flavor)
    assert table_flavor is not None, err

    config = table_flavor.block if block else table_flavor.inline
    assert config is not None, err

    return config
