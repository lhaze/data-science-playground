# -*- coding: utf-8 -*-
import numpy as np
from functools import wraps
from typing import (
    Any,
    Callable,
    Generator,
    NewType,
    Sequence,
    Tuple,
    Union,
)

from utils.functools import extended_to_sequence_of_inputs
from utils.itertools import transpose, xrange
from utils.timeline import Datapoints, Step, Timeline, TimelineIndex, Timepoint, Value

Argument = NewType('Argument', Any)
Function = Callable[[Union[Argument, Sequence[Argument]]], Value]


def build_timeline_interpolation(tl: Timeline, name: str, cast=None) -> Function:
    """
    Builds an interpolation of a property (specified by its name) basing on
    given Timeline.

    :param tl: the timeline of data
    :param name: the name of the property
    :param cast: function to cast values into
    """
    regular_datapoints, ephemeral_datapoints = tl.property_lists(name)
    step = tl.step
    return build_interpolation(regular_datapoints, ephemeral_datapoints, cast, step)


def build_interpolation(
        regular_datapoints: Datapoints,
        ephemeral_datapoints: Datapoints,
        cast: Function = None,
        step: Step = 1
) -> Function:
    """
    Builds an interpolation basing on a list of regular and a list of ephemeral
    values. Treats datapoints as separated by `step` intervals and uses `cast` function
    to cast values into.

    Interpolation is a function of timepoint or a sequence of timepoints. It
    returns a value at the timepoint in the former case or a sequence of
    values in the latter one.

    If the property is covered by ephemeral(s), value for is taken from the
    most specific ephemeral.

    >>> regular_datapoints = [
    ...    (TimelineIndex((1, 2)), 1),
    ...    (TimelineIndex((4, 6)), 3),
    ... ]
    >>> ephemeral_datapoints = [(TimelineIndex(5), 5)]
    >>> interpolation = build_interpolation(regular_datapoints, ephemeral_datapoints, cast=int)
    >>> list(interpolation((1, 2, 3, 4, 5, 6)))
    [1, 1, 2, 3, 5, 3]
    """
    interpolation = _build_regular_interpolation(regular_datapoints)
    if cast:
        interpolation = _build_cast_aspect(cast, interpolation)
    if ephemeral_datapoints:
        interpolation = _build_ephemeral_aspect(ephemeral_datapoints, interpolation, step)
    return interpolation


def _build_regular_interpolation(datapoints: Datapoints) -> Function:
    """
    >>> datapoints = [
    ...    (TimelineIndex((1, 2)), 1),
    ...    (TimelineIndex((4, 5)), 3),
    ... ]
    >>> interpolation = _build_regular_interpolation(datapoints)
    >>> list(interpolation((1, 2, 3, 4, 5)))
    [1.0, 1.0, 2.0, 3.0, 3.0]
    """
    interpolation_vectors = transpose(_expand_datapoints(datapoints))

    def interpolation(t):
        return np.interp(t, *interpolation_vectors)

    return interpolation


def _expand_datapoints(datapoints: Datapoints) -> Generator[Tuple[Timepoint, Value], None, None]:
    """
    Expands extended timespans (with the start and the end timepoint) into two pairs of
    Tuple[Timepoint, Value] which can be used as a
    """
    for timespan, value in datapoints:
        if timespan.end is None:
            yield (timespan.start, value)
        else:
            yield (timespan.start, value)
            yield (timespan.end, value)


def _build_ephemeral_aspect(datapoints: Datapoints, interpolation: Function, step: Step = 1):
    """
    Wraps `interpolation` with a function that overrides interpolation when
    ephemeral values are specified.

    >>> @extended_to_sequence_of_inputs
    ... def f(t):
    ...     return t + 0.5
    >>> datapoints = [
    ...    (TimelineIndex((1, 2)), 1),
    ...    (TimelineIndex((4, 5)), 3),
    ... ]
    >>> interpolation = _build_ephemeral_aspect(datapoints, f)
    >>> list(interpolation((1, 2, 3, 4, 5)))
    [1, 1, 3.5, 3, 3]
    """
    ephemerals = _build_ephemeral_dict(datapoints, step)

    @wraps(interpolation)
    @extended_to_sequence_of_inputs
    def ephemeral_wrapper(t):
        if t in ephemerals:
            # ephemeral case, return its value
            return ephemerals[t]
        # regular case, no ephemeral for this value, compute interpolation
        return interpolation(t)

    return ephemeral_wrapper


def _build_ephemeral_dict(datapoints: Datapoints, step: Step = 1) -> dict:
    """
    Builds a dict that defines all ephemeral values, based on an iterable of
    ephemeral datapoints.

    NB: asserts that datapoints are sorted

    >>> datapoints = [
    ...     (TimelineIndex((1, 5)), 1),
    ...     (TimelineIndex((2, 4)), 2),
    ...     (TimelineIndex((2, 3)), 3),
    ...     (TimelineIndex((6, 6)), 4),
    ... ]
    >>> _build_ephemeral_dict(datapoints)
    {1: 1, 2: 3, 3: 3, 4: 2, 5: 1, 6: 4}
    """
    assert datapoints
    ephemerals = {}
    for index, value in datapoints:
        end = index.start if index.end is None else index.end
        ephemerals.update((t, value) for t in xrange(index.start, end, step))
    return ephemerals


def _build_cast_aspect(cast: Function, interpolation: Function):
    """
    Wraps `interpolation` function with `cast` function. Respects
    the value vs. array of values duality.

    >>> @extended_to_sequence_of_inputs
    ... def f(t):
    ...     return t + 0.5
    >>> casted = _build_cast_aspect(int, f)
    >>> casted(0)
    0
    >>> casted(42)
    42
    >>> list(casted((0, 42)))
    [0, 42]
    """
    @wraps(interpolation)
    @extended_to_sequence_of_inputs
    def casting_wrapper(t: Argument):
        result = interpolation(t)
        return cast(result)

    return casting_wrapper
