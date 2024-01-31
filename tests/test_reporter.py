#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.reporter.reporter import OcxReporter


def test_report_count_elements(shared_datadir):
    model = shared_datadir / "m1.3Docx"
    reporter = OcxReporter(str(model))
    result = reporter.element_count()
    assert len(result) == 75


def test_report_count_filtered_elements(shared_datadir):
    model = shared_datadir / "m8.3Docx"
    reporter = OcxReporter(str(model))
    result = reporter.element_count(selection=['Panel', 'Plate', 'Stiffener'])
    assert len(result) == 3
