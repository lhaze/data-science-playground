from .base import Transformation


class LanguageMarker(Transformation):
    xpath = '//region[@class="DoCO:TextChunk"]'
