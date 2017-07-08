import copy

from cached_property import cached_property
from lxml.etree import _Element as Element, _ElementTree as ElementTree
import traits.api as traits


class Transformation(traits.HasTraits):
    """
    Mutator of lxml ElementTree.
    """

    # Definition
    xpath = traits.Str
    reconstruct_nodes = traits.Bool(default_value=False)

    # State
    tree = traits.Instance(ElementTree)
    original_nodes = traits.List(Element)
    transformed_nodes = traits.List(Element)

    @cached_property
    def _nodes(self):
        return self.tree.xpath(self.xpath)

    def __init__(self, tree):
        if not self.xpath:
            raise ValueError('`xpath` attribute needs to be provided')
        super(Transformation, self).__init__()
        self.tree = tree
        self.original_nodes = copy.deepcopy(self._nodes)

    def process(self):
        self.validate()
        self.transform()
        self.check()
        return self.tree

    def transform(self):
        """Main method of the class: defines the main loop and calls the hooks
        """
        for node in self._nodes:
            new_node = self.transform_node(node)
            self.transformed_nodes.append(new_node or node)
            if self.reconstruct_nodes:
                self.update_tree(node, new_node)

    def transform_node(self, node):
        raise NotImplementedError("A subclass should implement this method")

    def update_tree(self, old_node, new_node):
        self.tree.replace(old_node, new_node)
        '''
        parent = old_node.getparent()
        if parent is None:
            raise NotImplementedError("I won't remove root of the tree")
        previous = old_node.getprevious()
        if previous is not None:
            previous.tail = (previous.tail or '') + text
        else:
            parent.text = (parent.text or '') + text
        parent.remove(r)
        '''

    def validate(self):
        pass

    def check(self):
        for node in self.transformed_nodes:
            self.check_node(node)

    def check_node(self, node):
        pass
