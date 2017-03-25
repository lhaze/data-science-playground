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
from functools import total_ordering
from operator import attrgetter
from pprint import pformat
from ruamel import yaml
from typing import Any, Dict, Generator, Iterable, List, Tuple, Union

Timepoint = Union['numbers.Number', 'datetime.date']
Timespan = Union[Timepoint, Iterable[Timepoint]]


class Timeline(list):
    """
    An abstraction over a sequence of events with properities. The event might
    be described as being at a timepoint or extend between two timepoints.

    An event might be treated as an 'ephemeral' which
    means that it will be interpreted as a ephemeral change of property.
    This might be useful to describe changes that happens temporally and
    should not be taken as a datapoint while doing regular interpolation of
    property values.
    """

    @classmethod
    def load(cls, filename: str) -> 'Timeline':
        """
        Creates a Timeline from a YAML file defined by given filename.
        """
        with open(filename) as file:
            description = yaml.load(file)
        return cls.create(description)

    @classmethod
    def read(cls, string: str) -> 'Timeline':
        """
        Creates a Timeline from a string.

        >>> Timeline.read(__doc__)
        Timeline(
            1500: {'alive_population': 5000, 'mortality': 0.015, 'wraith_conversion_factor': 0.4},
            (1500, 1550): {'name': 'XV century', 'wraith_conversion_factor': 0.2},
            1600: {'alive_population': 7000},
            1800: {'mortality': 0.006, 'wraith_conversion_factor': 0.5},
        )
        """
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
            (TimelineEvent(t, v) for (t, v) in description.items()),
            key=attrgetter('_start')
        )
        return cls(items)

    def __repr__(self) -> str:
        content = (repr(event) for event in self)
        content_repr = "\n".join("    {},".format(line) for line in content)
        return "Timeline(\n{}\n)".format(content_repr)

    def property(self, name: str, ephemeral: bool=None) \
            -> Generator[Tuple[Any, Dict], None, None]:
        """
        Generator that iterates over property of given name.

        :param ephemeral: switches between only regular or only ephemeral events
        returned or both iff not specified (None).

        >>> tl = Timeline.read(__doc__)
        >>> list(tl.property('wraith_conversion_factor'))
        [(1500, 0.4), ((1500, 1550), 0.2), (1800, 0.5)]
        >>> list(tl.property('wraith_conversion_factor', ephemeral=True))
        [((1500, 1550), 0.2)]
        >>> list(tl.property('wraith_conversion_factor', ephemeral=False))
        [(1500, 0.4), (1800, 0.5)]
        """
        for event in self:
            if name in event.properties and \
                    (ephemeral is None or event.is_ephemeral() == ephemeral):
                yield (event.timespan, event.properties[name])

    def property_lists(self, name: str) -> Tuple[List, List]:
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
        return regular, ephemeral


@total_ordering
class TimelineEvent:
    """
    An object representation of timepoint of an event. It might be a single
    timepoint (int, float, date) or a pair of timepoints. The latter case
    describes an event extending over a period between the timepoints.
    """

    def __init__(self, timespan: Timespan, properties: Dict=None):
        """
        >>> TimelineEvent(42).timespan
        42
        >>> TimelineEvent((42, 45)).timespan
        (42, 45)
        """
        try:
            length = len(timespan)
        except TypeError:  # i.e. len(42)
            self._start = timespan
            self._end = None
        else:
            if length == 2:
                self._start, self._end = timespan
            else:
                raise NotImplementedError(
                    "Bad number of values for a key to Timeline: {}".
                        format(value)
                )
        self.properties = properties or {}

    @property
    def timespan(self):
        return self._start if self._end is None else (self._start, self._end)

    def __repr__(self):
        if self._end is None:
            k = repr(self._start)
        else:
            k = repr((self._start, self._end))
        return "{k}: {v}".format(k=k, v=pformat(self.properties))

    def __hash__(self):
        if self._end is None:
            return hash(self._start)
        return hash((self._start, self._end))

    def __eq__(self, other):
        """
        >>> i1 = TimelineEvent(2)
        >>> i2 = TimelineEvent(2)
        >>> i1 == i2
        True
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        other_end = getattr(other, '_end', None)
        return self._start == other._start and self._end == other_end

    def __lt__(self, other):
        """
        >>> i2 = TimelineEvent(2)
        >>> i3 = TimelineEvent(3)
        >>> i4 = TimelineEvent(4)
        >>> i3_4 = TimelineEvent((3, 4))
        >>> i3_5 = TimelineEvent((3, 5))
        >>> i2 < i3
        True
        >>> i3 < i3_5
        True
        >>> i3_5 > i3
        True
        >>> i4 > i3_5
        True
        >>> i3_4 < i3_5
        True
        """
        if not self._is_valid_operand(other):
            return NotImplemented
        if self._start == other._start:
            other_end = getattr(other, '_end', None)
            return (
                self._end is None or
                (other_end is not None and self._end < other_end)
            )
        return self._start < other._start

    def _is_valid_operand(self, other):
        return hasattr(other, '_start')

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
        return self.properties.get('ephemeral') or self._end is not None

    def is_containing(self, timepoint: Timepoint):
        """
        Iff event's timespan covers the given timepoint.

        >>> TimelineEvent(42).is_containing(42)
        True
        >>> TimelineEvent(42).is_containing(45)
        False
        >>> TimelineEvent((42, 45)).is_containing(42)
        True
        >>> TimelineEvent((42, 45)).is_containing(45)
        True
        """
        return self._start == timepoint if self._end is None \
            else self._start <= timepoint <= self._end
