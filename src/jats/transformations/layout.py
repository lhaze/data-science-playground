from .base import Transformation

class SecTransformation(Transformation):
    xpath = '//section'

    def transform_node(self, node):
        node.tag = "sec"
        node.attrib['jats_section'] = ''
        return node

    def check(self):
        """ All `xpath` tags were changed. """
        assert not self.tree.xpath(self.xpath)


class TitleTransformation(Transformation):
    xpath = '//h1[@class="DoCO:SectionTitle"]'


class ParagraphTransformation(Transformation):
    pass


class CleanAttributesTransformation(Transformation):
    """
    id, class, jats_*, page, column
    """
    def __init__(self, tree, node_type, attribute):
        super(CleanAttributesTransformation).__init__(tree)
        self.node_type = node_type
        self.attribute = attribute
