# -*- coding: utf-8 -*-
from lxml import etree


def load_xml(filepath):
    tree = etree.parse(filepath)
    assert len(tree.getroot())
    return tree
