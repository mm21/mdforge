from .element import BaseElement

__all__ = [
    "coerce_text",
]


def coerce_text(obj: str) -> BaseElement:
    """
    Create inline or block text, depending on the input.
    """

    # import just-in-time so all elements can use this module
    from .elements.block.basic import TextBlock
    from .elements.inline.text import Text

    return TextBlock(obj) if "\n" in obj else Text(obj)
