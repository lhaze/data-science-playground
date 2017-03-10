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
        ephemeral: true
1600:
    alive_population: 7000
1800:
    mortality: 0.006
    wraith_conversion_factor: 0.5
"""
from collections import OrderedDict
from functools import total_ordering
from operator import itemgetter
from pprint import pformat
from ruamel import yaml
from typing import Any, Dict, Generator, Iterable, List, Tuple, Union


class Timeline(OrderedDict):
    """
    An abstraction over a sequence of events with properities. The event might
    be described as being at a timepoint or extend between two timepoints.

    An event might be annotated as _ephemeral_ which means that it will be
    interpreted as a ephemeral change of property. This might be useful to
    describe changes that happens temporally and should not be taken as
    a datapoint while doing regular interpolation of property values.
    """

    # noinspection PyProtectedMember
    @total_ordering
    class Index:
        """
        An object representation of index of an event. It might be a single
        timepoint (int, float, date) or a pair of timepoints. The latter case
        describes an event extending over a period between the timepoints.
        """
        def __init__(self, value: Union['numbers.Number', 'datetime.date', Iterable]):
            """
            >>> Timeline.Index(42)
            42
            >>> Timeline.Index((42, 45))
            (42, 45)
            """
            try:
                length = len(value)
            except TypeError:  # i.e. len(42)
                self._start = value
                self._end = None
            else:
                if length == 2:
                    self._start, self._end = value
                else:
                    raise NotImplementedError(
                        "Bad number of values for a key to Timeline: {}".
                            format(value)
                    )

        def __repr__(self):
            if self._end is None:
                return repr(self._start)
            return tuple.__repr__((self._start, self._end))

        def __hash__(self):
            if self._end is None:
                return hash(self._start)
            return hash((self._start, self._end))

        def __eq__(self, other):
            """
            >>> i1 = Timeline.Index(2)
            >>> i2 = Timeline.Index(2)
            >>> i1 == i2
            True
            """
            if not self._is_valid_operand(other):
                return NotImplemented
            other_end = getattr(other, '_end', None)
            return self._start == other._start and self._end == other_end

        def __lt__(self, other):
            """
            >>> i2 = Timeline.Index(2)
            >>> i3 = Timeline.Index(3)
            >>> i4 = Timeline.Index(4)
            >>> i3_5 = Timeline.Index((3, 5))
            >>> i2 < i3
            True
            >>> i3_5 < i3
            True
            >>> i4 > i3_5
            True
            """
            if not self._is_valid_operand(other):
                return NotImplemented
            if self._start == other._start:
                other_end = getattr(other, '_end', None)
                return (
                    self._end is not None and
                    (other_end is None or self._end < other_end)
                )
            return self._start < other._start

        def _is_valid_operand(self, other):
            return hasattr(other, '_start')

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
            (1500, 1550): {'ephemeral': True, 'name': 'XV century', 'wraith_conversion_factor': 0.2},
            1500: {'alive_population': 5000, 'mortality': 0.015, 'wraith_conversion_factor': 0.4},
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
            ((cls.Index(k), v) for (k, v) in description.items()),
            key=itemgetter(0)
        )
        return cls(items)

    def __repr__(self) -> str:
        content = ("{k}: {v}".format(k=k, v=pformat(v)) for k, v in self.items())
        content_repr = "\n".join("    {},".format(line) for line in content)
        return "Timeline(\n{}\n)".format(content_repr)

    def property(self, name: str, ephemeral: bool=False) \
            -> Generator[Tuple[Any, Dict], None, None]:
        """
        Generator that iterates over property of given name. The 'ephemeral'
        boolean argument switches between only regular or only ephemeral events
        returned.

        >>> tl = Timeline.read(__doc__)
        >>> list(tl.property('alive_population'))
        [(1500, 5000), (1600, 7000)]
        >>> list(tl.property('wraith_conversion_factor', ephemeral=True))
        [((1500, 1550), 0.2)]
        """
        for index, properties in self.items():
            if name in properties and properties.get('ephemeral', False) == ephemeral:
                yield (index, properties[name])

    def property_lists(self, name: str, ephemeral: bool=None) -> Tuple[List, List]:
        """
        Returns two lists for a property of given name. The first one
        contains all regular events, the second - all ephemeral events.

        >>> tl = Timeline.read(__doc__)
        >>> tl.property_lists('wraith_conversion_factor')
        ([(1500, 0.4), (1800, 0.5)], [((1500, 1550), 0.2)])
        """
        regular = []
        ephemeral = []
        for index, properties in self.items():
            if name in properties:
                l = ephemeral if properties.get('ephemeral') else regular
                l.append((index, properties[name]))
        return regular, ephemeral
