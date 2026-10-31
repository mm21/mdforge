"""
Primitive Markdown elements which can be inserted into a document or section.
"""

__submodules__ = [
    "block",
    "inline",
]

# isort: off
# <AUTOGEN_INIT>
from .block import (
    Section,
    BlockImage,
    Paragraph,
    BlockText,
    ListItemType,
    ListItem,
    BulletList,
    NumberedList,
    BaseItemList,
    DefinitionItem,
    DefinitionList,
    Table,
    Cell,
    CellType,
    RowType,
)
from .inline import (
    Text,
    Emph,
    Strong,
    Underline,
    Strikethrough,
    Link,
    Ref,
    Newline,
    Span,
    InlineImage,
)

__all__ = [
    "Section",
    "BlockImage",
    "Paragraph",
    "BlockText",
    "ListItemType",
    "ListItem",
    "BulletList",
    "NumberedList",
    "BaseItemList",
    "DefinitionItem",
    "DefinitionList",
    "Table",
    "Cell",
    "CellType",
    "RowType",
    "Text",
    "Emph",
    "Strong",
    "Underline",
    "Strikethrough",
    "Link",
    "Ref",
    "Newline",
    "Span",
    "InlineImage",
]
# </AUTOGEN_INIT>
