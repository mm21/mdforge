"""
Utilities to normalize objects.

# TODO: move out to separate package w/similar utilities
"""

from dataclasses import dataclass
from typing import Any, Callable, Iterable, TypeVar

__all__ = [
    "CoerceSpec",
    "norm_obj",
    "norm_list",
]


ExpectT = TypeVar("ExpectT")
CoerceT = TypeVar("CoerceT", bound=ExpectT)


@dataclass
class CoerceSpec[CoerceT]:
    """
    Encapsulates type coercion info.
    """

    to_type: Callable[[Any], CoerceT]
    """
    Type to which to coerce, or a callable returning that type. Must take a 
    single argument of one of the type(s) given in `from_types`.
    """

    from_types: type[Any] | tuple[Any, ...]
    """
    Type(s) from which to coerce.
    """


def norm_obj(
    obj: Any, expect_type: type[ExpectT], coerce_spec: CoerceSpec | None = None
) -> ExpectT:
    """
    Normalize object to the expected type, coercing if applicable.
    """

    if isinstance(obj, expect_type):
        # already have expected type
        return obj
    else:

        if coerce_spec is None:
            # can't coerce
            raise ValueError(_err_str(obj, expect_type))

        if not isinstance(obj, coerce_spec.from_types):
            # not a type from which we can coerce
            raise ValueError(
                f"{_err_str(obj, expect_type)} and cannot be coerced from {coerce_spec.from_types}"
            )

        # return a new instance of the expected type
        return coerce_spec.to_type(obj)


def norm_list(
    objs: Any | Iterable[Any],
    expect_type: type[ExpectT],
    coerce_spec: CoerceSpec | None = None,
) -> list[ExpectT]:
    """
    Normalize object(s) to a list of the expected type, coercing if applicable.
    """

    objs_list: list[Any]

    # normalize to a list of any type
    # - exclude strings, which are also iterable
    if isinstance(objs, Iterable) and not isinstance(objs, str):
        # have an iterable of objects
        objs_list = list(objs)
    else:
        # have a single object
        objs_list = [objs]

    # normalize each object in list
    return [norm_obj(obj, expect_type, coerce_spec) for obj in objs_list]


def _err_str(obj: Any, expect_type: type[ExpectT]) -> str:
    return f"Object {obj} of type {type(obj)} is not of expected type {expect_type}"
