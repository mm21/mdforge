from __future__ import annotations

from .variant import FrameTableVariant, SectionConfig, SeparatorConfig

__all__ = [
    "MULTILINE_VARIANT",
    "GRID_VARIANT",
]

MULTILINE_VARIANT = FrameTableVariant(
    name="Pandoc multiline",
    header_section=SectionConfig(
        SeparatorConfig(),
        upper_sep=SeparatorConfig(outer_corner=""),
        lower_sep=SeparatorConfig(inner_corner=" ", outer_corner=""),
    ),
    content_section=SectionConfig(
        SeparatorConfig(line=None),
        upper_sep=SeparatorConfig(inner_corner=" ", outer_corner=""),
        lower_sep=SeparatorConfig(outer_corner=""),
    ),
    align_space=True,
    cell_sep=" ",
    row_leading_sep="",
    row_trailing_sep="",
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

GRID_VARIANT = FrameTableVariant(
    name="Pandoc grid",
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
    align_char=":",
    cell_sep=" | ",
    row_leading_sep="| ",
    row_trailing_sep=" |",
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
