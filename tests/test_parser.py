#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.parser.parser import OcxParser


def test_parse(shared_datadir):
    parser = OcxParser()
    model = shared_datadir / "m1_pp.3Docx"
    assert parser.parse(str(model.resolve()))
