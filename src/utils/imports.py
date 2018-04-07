# -*- coding: utf-8 -*-
import os
import sys
import typing as t


def import_entity(entity_path: str) -> t.Any:
    module_name, class_name = entity_path.split(':')
    entity_module = __import__(module_name, globals(), locals(), (class_name, ))
    return getattr(entity_module, class_name)


def get_all_names(_file, _name, _filter=lambda obj: True):
    """
    Util for returning from all submodules all objects fulfilling the `_filter` condition.
    Use it in the __init__.py using following idiom:
        a_dict = get_all_names(__file__, __name__, a_condition)
    Supports __all__ attribute of the submodules.
    """
    path = os.path.dirname(os.path.abspath(_file))
    parent_module = sys.modules[_name]

    result = {}
    for py in [filename[:-3] for filename in os.listdir(path)
               if filename.endswith('.py') and filename != '__init__.py']:
        module = __import__('.'.join([_name, py]), fromlist=[py])
        module_names = getattr(module, '__all__', None) or dir(module)
        objects = dict(
            (name, getattr(module, name))
            for name in module_names
            if not name.startswith('_')
        )
        for name, obj in objects.items():
            if hasattr(parent_module, name) and \
               getattr(parent_module, name) is not obj:
                msg = (
                    "Function get_all_names hit upon conflicting "
                    "names. '{0}' is already imported to {1} module."
                ).format(name, module)
                import warnings
                warnings.warn(msg)
            if _filter(obj):
                result[name] = obj
    return result
