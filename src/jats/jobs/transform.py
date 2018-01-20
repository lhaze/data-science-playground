# -*- coding: utf-8 -*-
from functools import partial, reduce
from lxml import etree

from jats.transformations import Transformation
from utils.xml import load_xml

from .. import make_task_dir, path


def transformation_job_constructor(transformations):
    """
    Builds a function of
    :param transformations:
    :return: a function od **description -> **other_description
    """
    if issubclass(transformations, Transformation):
        # not an iterable but a single Transformation subclass
        # let's make a list
        transformations = [transformations]
    process = process_constructor(transformations)
    # process := lambda tree, **description -> tree
    return partial(xml_aspect, process=process)


def process_constructor(transformations):
    """

    :param transformations: iterable of classes defining transformations to be
        done: a class with ``process`` method.
    :return: function: tree, **description -> tree which chaines ``process``
        methods of instances of classes taken from ``transformations``
    """
    transform = lambda tree, transformation, **description: \
        transformation(tree, **description).process()
    return lambda tree, **description: \
        reduce(partial(transform, **description),
               transformations,
               tree)


def xml_aspect(process, **description):
    tree = load_xml(description['input'])

    process = partial(process, tree=tree)

    def t():
        with open(description['output'], 'w') as output:
            output.write(etree.tostring(tree))
    return description


def description_aspect(**description):
    description['task_done'] += 1
    output_dir = make_task_dir(
        doc_name=description['doc_name'],
        task_nr=description['task_done'],
        task_name=description['name']
    )
    description['output'] = path(output_dir, description['xml_name'])
    return description

# TODO ruffus_aspect
