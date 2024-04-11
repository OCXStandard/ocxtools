#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.parser.parser import OcxParser
from tests.conftest import TEST_MODEL


def test_parse(shared_datadir):
    parser = OcxParser()
    model = shared_datadir / TEST_MODEL
    assert parser.parse(str(model.resolve()))
