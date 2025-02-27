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


def norm_obj[
    ExpectT, CoerceT
](
    obj: Any,
    expect_type: type[ExpectT],
    *coerce_specs: CoerceSpec[CoerceT],
) -> ExpectT:
    """
    Normalize object to the expected type, coercing if applicable.
    """

    if isinstance(obj, expect_type):
        # already have expected type
        return obj
    else:

        # try to coerce using provided specs
        for coerce_spec in coerce_specs:

            if isinstance(obj, coerce_spec.from_types):
                # coerce using this spec
                obj_norm = coerce_spec.to_type(obj)

                if not isinstance(obj_norm, expect_type):
                    note = f"and coercion {coerce_spec} failed (got {obj_norm})"
                    raise ValueError(_err_str(obj, expect_type, note))

                return obj_norm

        # could not coerce
        if len(coerce_specs):
            specs_str = ", ".join(str(spec) for spec in coerce_specs)
            note = f"and cannot be coerced from {specs_str}"
        else:
            note = None
        raise ValueError(_err_str(obj, expect_type, note))


def norm_list[
    ExpectT, CoerceT
](
    objs: Any | Iterable[Any],
    expect_type: type[ExpectT],
    *coerce_specs: CoerceSpec[CoerceT],
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
    return [norm_obj(obj, expect_type, *coerce_specs) for obj in objs_list]


def _err_str(
    obj: Any, expect_type: type[ExpectT], note: str | None = None
) -> str:
    note_norm = f" {note}" if note else ""
    return f"Object {obj} of type {type(obj)} is not of expected type {expect_type}{note_norm}"
