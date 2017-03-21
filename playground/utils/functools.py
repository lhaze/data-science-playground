# -*- coding: utf-8 -*-
from collections import Sequence
import numpy as np
from typing import Any, Iterable, Callable, NewType, Sequence, Union

from playground.utils.timeline import Timeline

Value = NewType('Value', Any)
Argument = NewType('Argument', Any)
Function = Callable[[Union[Argument, Sequence[Argument]]], Value]


def transpose(items: Iterable) -> list:
    """
    Transforms iterable of datapoints into vectors of

    >>> transpose([(1, 1), (2, 2), (3, 3)])
    [(1, 2, 3), (1, 2, 3)]
    """
    return list(zip(*items))


def _choose_ephemeral(datapoints, t):
    """
    Chooses right ephemeral from ephemeral datapoints according to t value.

    >>> data = {
    ...     (1, 5): 1,
    ...     (2, 4): 2,
    ...     (2, 3): 3,
    ...     (6, 6): 4,
    ... }
    >>> datapoints = [(Timeline.Index(i), v) for i, v in data.items()]
    >>> datapoints.sort()
    >>> _choose_ephemeral(datapoints, 0) is None
    True
    >>> _choose_ephemeral(datapoints, 1)
    1
    """
    return None


def _build_ephemeral_aspect(datapoints: Iterable, interpolation: Function):
    """
    Wraps `interpolation` with a function that overrides interpolation when
    ephemeral values are specified.

    >>> def interpolation(t):
    ...     if isinstance(t, Sequence):
    ...         return [interpolation(v) for v in t]
    ...     return t + 0.5

    """
    def ephemeral_wrapper(t):
        ephemeral = _choose_ephemeral(datapoints, t)
        if ephemeral is not None:
            # ephemeral case, return its value
            return ephemeral
        # regular case, no ephemeral for this value, compute interpolation
        return interpolation(t)

    return ephemeral_wrapper


def _build_cast_aspect(cast: Function, interpolation: Function):
    """
    Wraps `interpolation` function with `cast` function. Respects
    the value vs. array of values duality.

    >>> def interpolation(t):
    ...     if isinstance(t, Sequence):
    ...         return [interpolation(v) for v in t]
    ...     return t + 0.5
    >>> casted = _build_cast_aspect(int, interpolation)
    >>> casted(0)
    0
    >>> casted(42)
    42
    >>> casted((0, 42))
    [0, 42]
    """
    def casting_wrapper(t: Argument):
        result = interpolation(t)
        if isinstance(result, Sequence):
            return list(cast(value) for value in result)
        return cast(result)

    return casting_wrapper


def build_interpolation(tl: Timeline, name: str, cast=None) \
        -> Function:
    """
    Returns interpolation of a property (specified by its name), based on
    given Timeline.

    Interpolation is a function of timepoint or a sequence of timepoints. It
    returns a value at the timepoint in the former case or a sequence of
    values in the latter one.

    If the property is covered by ephemeral(s), value for is taken from the
    most specific ephemeral.
    """
    regular_datapoints, ephemeral_datapoints = tl.property_lists(name)
    interpolation_vectors = transpose(regular_datapoints)

    def interpolation(t):
        return np.interp(t, *interpolation_vectors)

    if cast:
        interpolation = _build_cast_aspect(cast, interpolation)

    if ephemeral_datapoints:
        interpolation = _build_ephemeral_aspect(ephemeral_datapoints, interpolation)

    return interpolation
