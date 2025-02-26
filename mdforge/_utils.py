from .element import BaseElement

__all__ = [
    "coerce_text",
    "wrap_para_cond",
]


def coerce_text(obj: str) -> BaseElement:
    """
    Create inline or block text, depending on the input.
    """

    # import just-in-time so all elements can use this module
    from .elements.block.basic import BlockText
    from .elements.inline.text import Text

    return BlockText(obj) if "\n" in obj else Text(obj)


def wrap_para_cond(lines: list[str]):
    """
    Wrap lines in an HTML paragraph in-place, if there are no blank lines.
    """
    assert len(lines)
    if any(line.strip() == "" for line in lines):
        return

    lines[0] = f"<p>{lines[0]}"
    lines[-1] = f"{lines[-1]}</p>"
