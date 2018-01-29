# -*- coding: utf-8 -*-
"""
# Sample timeline YAML description:
1500:
    alive_population: 5000
    mortality: 0.015
    wraith_conversion_factor: 0.4
[1500, 1550]:
        name: XV century
        wraith_conversion_factor: 0.2
1600:
    alive_population: 7000
1800:
    mortality: 0.006
    wraith_conversion_factor: 0.5
"""
from datetime import date, timedelta
from functools import total_ordering
from numbers import Number
from operator import attrgetter
from pprint import pformat
from ruamel import yaml
from typing import (
    Any,
    Dict,
    Generator,
    List,
    Sequence,
    Tuple,
    Union,
)

from utils.functools import Value

Timepoint = Union[Number, date]
Step = Union[Number, timedelta]
Timespan = Union[Timepoint, Tuple[Timepoint, Timepoint]]
Datapoint = Tuple['TimelineIndex', Value]
Datapoints = Sequence[Datapoint]
PropertyGenerator = Generator[Datapoint, None, None]


class Timeline(list):
    """
    An abstraction over a sequence of events with properties. The event might
    be described as being at a timepoint or extend between two timepoints.

    An event might be treated as an 'ephemeral' which
    means that it will be interpreted as a non-continuous, ad-hoc change of property.
    This might be useful to describe changes that happens temporally and
    should not be taken as a datapoint while doing regular interpolation of
    property values.
    """
    step = 1

    @classmethod
    def load(cls, filename: str) -> 'Timeline':
        """
        Creates a Timeline from a YAML file defined by given filename.
        """
        with open(filename) as file:
            # noinspection PyTypeChecker
            description = yaml.load(file, Loader=yaml.Loader)
        return cls.create(description)

    @classmethod
    def read(cls, string: str) -> 'Timeline':
        """
        Creates a Timeline from a string.

        >>> Timeline.read(__doc__)
        Timeline(
            (1500, 1550): {'name': 'XV century', 'wraith_conversion_factor': 0.2},
            1500: {'alive_population': 5000, 'mortality': 0.015, 'wraith_conversion_factor': 0.4},
            1600: {'alive_population': 7000},
            1800: {'mortality': 0.006, 'wraith_conversion_factor': 0.5},
        )
        """
        # noinspection PyTypeChecker
        description = yaml.load(string, Loader=yaml.Loader)
        return cls.create(description)

    @classmethod
    def create(cls, description: Dict) -> 'Timeline':
        """
        Creates a Timeline based on a dict.

        >>> Timeline.create({1500: {'foo': 'bar'}, (1600, 1700): {'foo': 'baz'}})
        Timeline(
            1500: {'foo': 'bar'},
            (1600, 1700): {'foo': 'baz'},
        )
        """
        items = sorted(
            (TimelineEvent(*event) for event in description.items()),
            key=attrgetter('timespan')
        )
        return cls(items)

    @property
    def start(self) -> Timepoint:
        return self[0].timespan.start

    @property
    def end(self) -> Timepoint:
        timespan = self[-1].timespan
        return timespan.end if timespan.end is not None else timespan.start

    def __repr__(self) -> str:
        if not self:
            return "Timeline()"
        content = (repr(event) for event in self)
        content_repr = "\n".join("    {},".format(line) for line in content)
        return "Timeline(\n{}\n)".format(content_repr)

    def property(self, name: str, ephemeral: bool=None) -> PropertyGenerator:
        """
        Generator that iterates over property of given name.

        :param name: name of the property
        :param ephemeral: switches between only regular or only ephemeral
            events returned or both iff not specified (None).

        >>> tl = Timeline.read(__doc__)
        >>> list(tl.property('wraith_conversion_factor'))
        [((1500, 1550), 0.2), (1500, 0.4), (1800, 0.5)]
        >>> list(tl.property('wraith_conversion_factor', ephemeral=True))
        [((1500, 1550), 0.2)]
        >>> list(tl.property('wraith_conversion_factor', ephemeral=False))
        [(1500, 0.4), (1800, 0.5)]
        """
        for event in self:
            if name in event.properties and \
                    (ephemeral is None or event.is_ephemeral() == ephemeral):
                yield (event.timespan, event.properties[name])

    def property_lists(self, name: str) -> Tuple[Datapoints, Datapoints]:
        """
        Returns two lists for a property of given name. The first one
        contains all regular events, the second - all ephemeral events.

        >>> tl = Timeline.read(__doc__)
        >>> tl.property_lists('wraith_conversion_factor')
        ([(1500, 0.4), (1800, 0.5)], [((1500, 1550), 0.2)])
        """
        regular = []
        ephemeral = []
        for event in self:
            if name in event.properties:
                l = ephemeral if event.is_ephemeral() else regular
                l.append((event.timespan, event.properties[name]))
        assert regular, "Property name not found in the timeline"
        return regular, ephemeral


@total_ordering
class TimelineEvent:
    """
    Represents an event in a timeline. It is described with timespan and some properties.
    The timespan might be a single timepoint (int, float, date) or a pair of timepoints
    (the start and the end of the event). The latter case describes an event extending over
    a period between the timepoints.
    """
    __slots__ = ("timespan", "properties")

    def __init__(self, timespan: Timespan, properties: Dict=None):
        """
        >>> TimelineEvent(42).timespan
        42
        >>> TimelineEvent((42, 45)).timespan
        (42, 45)
        """
        self.timespan = TimelineIndex(timespan)
        self.properties = properties or {}

    def __repr__(self):
        return "{k}: {v}".format(k=self.timespan, v=pformat(self.properties))

    def __eq__(self, other: Any) -> bool:
        """
        >>> i1 = TimelineEvent(2)
        >>> i2 = TimelineEvent(2)
        >>> i1 == i2
        True
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.timespan == other.timespan

    def __lt__(self, other: Any) -> bool:
        """
        >>> i2 = TimelineEvent(2)
        >>> i3 = TimelineEvent(3)
        >>> i4 = TimelineEvent(4)
        >>> i3_4 = TimelineEvent((3, 4))
        >>> i3_5 = TimelineEvent((3, 5))
        >>> i2 < i3
        True
        >>> i3 > i3_5
        True
        >>> i3_5 < i3
        True
        >>> i4 > i3_5
        True
        >>> i3_4 > i3_5
        True
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.timespan < other.timespan

    @staticmethod
    def _is_valid_operand(other):
        return hasattr(other, 'timespan')

    def is_ephemeral(self):
        """
        By default, only extended events are treated as ephemeral
        (unless properities states otherwise).

        >>> TimelineEvent(42).is_ephemeral()
        False
        >>> TimelineEvent((42, 45)).is_ephemeral()
        True
        >>> TimelineEvent(42, {'ephemeral': True}).is_ephemeral()
        True
        >>> TimelineEvent((42, 45), {'ephemeral': False}).is_ephemeral()
        True
        """
        return self.properties.get('ephemeral') or \
            self.timespan.end is not None


@total_ordering
class TimelineIndex:
    """
    Represents an index of the timeline. It might be a single timepoint (int, float, date)
    or a pair of timepoints (the start and the end of the event).
    """
    __slots__ = ('start', 'end')

    def __init__(self, timespan: Timespan):
        """
        >>> TimelineIndex(42)
        42
        >>> TimelineIndex((42, 45))
        (42, 45)
        """
        try:
            start, end = timespan
        except (ValueError, TypeError):  # i.e. 42 or None
            start = timespan
            end = None
        else:
            if start == end:
                end = None
        assert end is None or start < end
        self.start, self.end = start, end

    def __repr__(self):
        if self.end is None:
            return repr(self.start)
        return repr((self.start, self.end))

    def __hash__(self):
        if self.end is None:
            return hash(self.start)
        return hash((self.start, self.end))

    @staticmethod
    def _is_valid_operand(other):
        return hasattr(other, 'start') and hasattr(other, 'end')

    def __eq__(self, other: Any) -> bool:
        """
        >>> i1 = TimelineIndex(2)
        >>> i2 = TimelineIndex(2)
        >>> i1 == i2
        True
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        other_end = getattr(other, 'end', None)
        return self.start == other.start and self.end == other_end

    def __lt__(self, other: Any) -> bool:
        """
        >>> i2 = TimelineIndex(2)
        >>> i3 = TimelineIndex(3)
        >>> i4 = TimelineIndex(4)
        >>> i3_4 = TimelineIndex((3, 4))
        >>> i3_5 = TimelineIndex((3, 5))
        >>> i2 < i3
        True
        >>> i3 > i3_5
        True
        >>> i3_5 < i3
        True
        >>> i4 > i3_5
        True
        >>> i3_4 > i3_5
        True
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        if self.start == other.start:
            other_end = getattr(other, 'end', None)
            return (
                self.end is not None and
                (other_end is None or self.end > other_end)
            )
        return self.start < other.start

    def __sub__(self, other: Any) -> List['TimelineIndex']:
        """
        >>> TimelineIndex((1, 4)) - TimelineIndex((1, 5))
        []
        >>> TimelineIndex((1, 4)) - TimelineIndex((3, 5))
        [(1, 2)]
        >>> TimelineIndex((1, 4)) - TimelineIndex((1, 3))
        [4]
        >>> TimelineIndex((1, 4)) - TimelineIndex(2)
        [1, (3, 4)]
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        self_end = self.start if self.end is None else self.end
        other_end = other.start if other.end is None else other.end
        if other_end < self.start or other.start > self_end:
            # non-overlapping case; move along, nothing to modify here
            return [self]
        result = []
        if self.start < other.start:
            # case 'before'
            result.append(self.__class__((self.start, other.start - 1)))
        if other_end < self_end:
            # case 'after'
            result.append(self.__class__((other_end + 1, self_end)))
        # iff none of the above: the case where nothing remains
        # 'other' completely covers 'self'
        return result

    def is_containing(self, timepoint: Timepoint) -> bool:
        """
        Iff index' timespan covers the given timepoint.

        >>> TimelineIndex(42).is_containing(42)
        True
        >>> TimelineIndex(42).is_containing(45)
        False
        >>> TimelineIndex((42, 45)).is_containing(42)
        True
        >>> TimelineIndex((42, 45)).is_containing(45)
        True
        """
        return self.start == timepoint if self.end is None \
            else self.start <= timepoint <= self.end
