"""
Custom exceptions.
"""

__all__ = [
    "ValidationError",
    "RenderError",
    "RenderWarning",
]


class ValidationError(Exception):
    """
    Raised upon element instantiation if input is invalid.
    """


class RenderError(Exception):
    """
    Raised upon rendering if input is invalid, possibly dependent on the flavor used for
    rendering.
    """


class RenderWarning(UserWarning):
    """
    Issued upon rendering for valid but likely unintended input, e.g. a skipped heading
    level.
    """
