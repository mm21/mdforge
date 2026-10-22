"""
MDForge: Forge Markdown files in a Python way.
"""

__submodules__ = [
    "types",
    "document",
    "element",
    "container",
    "elements",
    "exceptions",
]

# isort: off
# <AUTOGEN_INIT>
from .types import (
    FlavorType,
    AlignType,
)
from .document import (
    Document,
)
from .element import (
    BaseElement,
    BaseInlineElement,
    BaseBlockElement,
    Attributes,
)
from .container import (
    InlineContainer,
    BlockContainer,
)
from .elements import (
    Section,
    Heading,
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
from .exceptions import (
    ValidationError,
    RenderError,
)

__all__ = [
    "FlavorType",
    "AlignType",
    "Document",
    "BaseElement",
    "BaseInlineElement",
    "BaseBlockElement",
    "Attributes",
    "InlineContainer",
    "BlockContainer",
    "Section",
    "Heading",
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
    "ValidationError",
    "RenderError",
]
# </AUTOGEN_INIT>
