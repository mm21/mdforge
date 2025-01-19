from __future__ import annotations

from .frame import FrameTableConfig, SectionConfig, SeparatorConfig

__all__ = [
    "MULTILINE_CONFIG",
    "GRID_CONFIG",
]

MULTILINE_CONFIG = FrameTableConfig(
    header_section=SectionConfig(
        SeparatorConfig(), lower_sep=SeparatorConfig(inner_corner=" ")
    ),
    content_section=SectionConfig(
        SeparatorConfig(line=None),
        lower_sep=SeparatorConfig(),
        upper_sep=SeparatorConfig(inner_corner=" "),
    ),
    footer_section=SectionConfig(SeparatorConfig()),
    align_space=True,
)
"""
Pandoc multiline table. 

For example:

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
"""

GRID_CONFIG = block = FrameTableConfig(
    header_section=SectionConfig(
        SeparatorConfig(corner="+"),
        lower_sep=SeparatorConfig(line="=", corner="+"),
    ),
    content_section=SectionConfig(SeparatorConfig(corner="+")),
    footer_section=SectionConfig(
        SeparatorConfig(corner="+"),
        lower_sep=SeparatorConfig(line="=", corner="+"),
        upper_sep=SeparatorConfig(line="=", corner="+"),
    ),
    cell_sep="|",
    align_char=":",
)
"""
Pandoc grid table.

For example:

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
"""
