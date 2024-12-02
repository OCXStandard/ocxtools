#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
import pytest

from ocxtools.reporter.reporter import OcxReporter, ReportType
from tests.conftest import TEST_MODEL


def test_report_count_elements(shared_datadir):
    model = shared_datadir / TEST_MODEL
    reporter = OcxReporter()
    reporter.parse_model(str(model.resolve()))
    result = reporter.element_count(str(model))
    assert result.count == 289


def test_report_count_filtered_elements(shared_datadir):
    model = shared_datadir / TEST_MODEL
    reporter = OcxReporter()
    reporter.parse_model(str(model.resolve()))
    result = reporter.element_count(selection=['Panel', 'Plate', 'Stiffener'])
    assert result.count == 289


@pytest.mark.skip
def test_dataframe_header(shared_datadir):
    model = shared_datadir / TEST_MODEL
    reporter = OcxReporter()
    df = reporter.dataframe(str(model.resolve()), ocx_type=ReportType.HEADER)
    assert df.columns == 7


@pytest.mark.skip
def test_dataframe_plate(shared_datadir):
    model = shared_datadir / TEST_MODEL
    reporter = OcxReporter()
    report = reporter.dataframe(str(model.resolve()), ocx_type=ReportType.PLATE)
    df = report.elements
    assert df.guidref[0] == '62e35289-183a-484c-8c0a-1c01260187d1'
