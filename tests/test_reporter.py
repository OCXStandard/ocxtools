#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.reporter.reporter import OcxReporter
from ocxtools.parser.parser import OcxNotifyParser


def test_report_count_elements(shared_datadir):
    model = shared_datadir / "m1.3Docx"
    parser = OcxNotifyParser()
    reporter = OcxReporter(parser)
    parser.parse(str(model.resolve()))
    result = reporter.element_count()
    assert len(result) == 74


def test_report_count_filtered_elements(shared_datadir):
    model = shared_datadir / "m8.3Docx"
    parser = OcxNotifyParser()
    reporter = OcxReporter(parser)
    parser.parse(str(model.resolve()))
    result = reporter.element_count(selection=['Panel', 'Plate', 'Stiffener'])
    assert len(result) == 3
