# coding=utf-8
import re

from .base import Transformation


# Alphabet Unicode character
ALPHA = r'[^\W\d_]'
# '- ' between two alpahber Unicode characters (not matching the two)
WORD_BREAK_RE = re.compile(r'(?<={a})- (?={a})'.format(a=ALPHA))


def remove_word_breaks(text):
    return WORD_BREAK_RE.sub('', text)


class WordBreakTransformation(Transformation):
    """
    Problems:
    * Pauza nierozróżnialna od dywiza
        odległość głowa–spojenie (head–\nsymphysis distance, HSD)
    """

    xpath = '//region[@class="DoCO:TextChunk"]'

    def validate(self):
        # TODO
        pass

    def transform_node(self, node):
        pass

    def check(self):
        """No substring recognizeable as a word break in the whole doc"""
        serialized = self.tree.tostring()
        assert not WORD_BREAK_RE.match(serialized)

    def check_node(self, node):
        pass


class MarkerTransformation(Transformation):

    xpath = '//region[@class="DoCO:TextChunk"]'

    def transform_node(self, node):
        marker_seeker = lambda type_: node.xpath(
            '//marker[@type="{}"]'.format(type_))
        markers = {
            'block': marker_seeker('block'),
            'column': marker_seeker('column'),
            'page': marker_seeker('page'),
        }
