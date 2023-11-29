#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
import json
from pathlib import Path
# Project imports
from ocxtools.parser.parser import OcxParser
from ocxtools.serializer.serializer import Serializer


def test_serialize_json(shared_datadir, data_regression):
    parser = OcxParser()
    model = shared_datadir / "box.3Docx"
    ocxxml = parser.parse(str(model.resolve()))
    serializer = Serializer(ocxxml)
    result = serializer.serialize_json()
    data_regression.check(json.loads(result))


def test_serialize_xml(shared_datadir):
    parser = OcxParser()
    model = shared_datadir / "box.3Docx"
    ocxxml = parser.parse(str(model.resolve()))
    serializer = Serializer(ocxxml)
    result = serializer.serialize_xml()
    assert '?xml version' in result
