import os
import requests

from src.jats import PdfxError
from src.utils.os import path

from .. import make_task_dir


PDFX_SERVICE_URL = 'http://pdfx.cs.man.ac.uk/'
TASK_NR = 1
TASK_NAME = 'pdfx_xml'


def send_to_pdfx(filepath):
    data = {
        'sent_splitter': 'punkt',
        'ref_doi': 'ref_doi',
    }
    headers = {"Content-Type": "application/pdf"}

    try:
        with open(filepath, 'rb') as pdf:
            files = {'userfile': pdf}
            resp = requests.post(
                PDFX_SERVICE_URL,
                data=data, files=files, headers=headers)
    except OSError:
        resp = None
    return resp


def get_xml_from_pdfx(input_path):
    assert os.path.isfile(input_path)

    resp = send_to_pdfx(input_path)
    if not resp or resp.status_code != 200:
        raise PdfxError("PDFX error:\n{}".format(resp.content))

    input_filename = input_path.rsplit(os.path.sep, 1)[-1] \
        if os.path.sep in input_path else input_path
    doc_name, _ = input_filename.rsplit('.', 1)
    xml_name = doc_name + ".xml"
    output_dir = make_task_dir(doc_name, TASK_NR, TASK_NAME)
    output_path = path(output_dir, xml_name)

    with open(output_path, 'w') as output:
        output.write(resp.content)
    assert os.path.isfile(output_path)

    return {
        'origin': input_path,
        'doc_name': doc_name,
        'xml_name': xml_name,
        'task_done': 1,
        'output': output_path,
    }
