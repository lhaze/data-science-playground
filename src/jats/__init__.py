# -*- coding: utf-8 -*-
from utils.oss import ensure_dir_exists, path


CODE_DIR = ensure_dir_exists(path(__file__, '..', '..'))
PROJECT_DIR = ensure_dir_exists(path(CODE_DIR, '..'))
WORKBENCH_DIR = ensure_dir_exists(path(PROJECT_DIR, 'workbench'))
EXAMPLE_XML_PATH = path(WORKBENCH_DIR, '125-136_jou61-1-pdfx_xml', '125-136_jou61.xml')


class PdfxError(Exception):
    pass


def make_task_dir(doc_name, task_nr, task_name): \
    return ensure_dir_exists(
        path(WORKBENCH_DIR, '{}-{}-{}'.format(
            doc_name, task_nr, task_name
        ))
    )


def get_example_tree():
    from src.utils.xml import load_xml
    return load_xml(EXAMPLE_XML_PATH)
