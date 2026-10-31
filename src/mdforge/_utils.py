import warnings

from .element import BaseElement, BaseInlineElement
from .exceptions import RenderError, RenderWarning, ValidationError

__all__ = [
    "coerce_text",
    "coerce_inline_text",
    "wrap_para_cond",
    "validate_level",
    "check_level",
]

MAX_LEVEL: int = 6
"""
Maximum heading level supported by markdown.
"""


def coerce_text(obj: str) -> BaseElement:
    """
    Create inline or block text, depending on the input.
    """
    from .elements.block.text import BlockText
    from .elements.inline.text import Text

    return BlockText(obj) if "\n" in obj else Text(obj)


def coerce_inline_text(obj: str, allow_multiline: bool = False) -> BaseInlineElement:
    """
    Wrap text with inline element, validating based on whether newlines (non-consecutive
    only) are allowed.
    """
    from .container import InlineContainer
    from .elements.inline.text import Newline, Text

    # get lines
    lines = obj.split("\n")

    # check for blank lines, allowing single-line text to be only whitespace
    if len(lines) > 1 and any(line.strip() == "" for line in lines):
        raise ValidationError(f"Input text cannot contain blank lines: {obj}")

    if len(lines) > 1 and allow_multiline:

        elements: list[BaseInlineElement] = []

        # split lines into a container of text and newline elements
        for i, line in enumerate(lines):
            elements.append(Text(line))
            if i != len(lines) - 1:
                elements.append(Newline())

        return InlineContainer(*elements)

    return Text(obj)


def wrap_para_cond(lines: list[str]):
    """
    Wrap lines in an HTML paragraph in-place, if there are no blank lines.
    """
    assert len(lines)
    if any(line.strip() == "" for line in lines):
        return

    lines[0] = f"<p>{lines[0]}"
    lines[-1] = f"{lines[-1]}</p>"


def validate_level(level: int | None):
    """
    Ensure the explicit level, if given, is supported by markdown.
    """
    if level is not None and not 1 <= level <= MAX_LEVEL:
        raise ValidationError(f"Level must be between 1 and {MAX_LEVEL}, got {level}")


def check_level(desc: str, level: int, expected: int):
    """
    Check the level of an element against the level expected from its placement: fail if
    it's not nested in its containing level, or warn if it skips levels.
    """
    if level < expected:
        raise RenderError(
            f"Level {level} of {desc} must be at least {expected} based on its placement"
        )
    if level > expected:
        warnings.warn(
            f"Level {level} of {desc} skips levels, expected {expected} based on its placement",
            RenderWarning,
        )
