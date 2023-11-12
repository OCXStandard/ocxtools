#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.parser import OcxParser


def test_parse(shared_datadir):
    parser = OcxParser()
    model = shared_datadir / 'midship.3Docx'
    assert parser.parse(model.resolve())


def test_iterator(shared_datadir):
    parser = OcxParser()
    model = shared_datadir / 'midship.3Docx'
    iterable = parser.iterator(model.resolve())
    assert hasattr(iterable, '__iter__')



