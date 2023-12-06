#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.utils.utilities import SourceValidator


def test_filter_files(shared_datadir, data_regression):
    result = {file.name: file.name for file in SourceValidator.filter_files(str(shared_datadir), '*.3docx')}
    data_regression.check(result)


def test_is_url():
    assert SourceValidator.is_url("file://models/m1.3docx")


def test_is_directory(shared_datadir):
    assert SourceValidator.is_directory(str(shared_datadir))
