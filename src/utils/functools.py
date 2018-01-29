# -*- coding: utf-8 -*-
from typing import (
    Any,
    Callable,
    NewType,
    Sequence,
    Union,
)

from utils.itertools import is_sequence

Argument = NewType('Argument', Any)
Arguments = Union[Argument, Sequence[Argument]]
Value = NewType('Value', Any)
Function = Callable[[Arguments], Value]


def extended_to_sequence_of_inputs(f: Function):
    """
    Extends given function to return generator of return values iff it is
    given an iterable of inputs.
    """
    def wrapper(t: Arguments):
        if is_sequence(t):
            return (f(v) for v in t)
        return f(t)

    return wrapper
