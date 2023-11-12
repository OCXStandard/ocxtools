#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.ocx_version_manager import VersionManager
from loguru import logger

def test_dynamic_import_v286():
    assert (VersionManager.dynamic_import('ocx', '2.8.6')) is not None


def test_dynamic_import_v300b0():
    assert (VersionManager.dynamic_import('ocx', '3.0.0b0')) is not None


def test_dynamic_import_v300b3():
    assert (VersionManager.dynamic_import('ocx', '3.0.0b3')) is not None


def test_get_all_class_names(data_regression):
    result = VersionManager.get_all_class_names('ocx', '2.8.6')
    data_regression.check(result)


def test_compare_class_names(data_regression):
    result = VersionManager.compare_class_names('2.8.6', '3.0.0b3')
    data_regression.check(result)


def test_get_meta_data_v286(data_regression):
    data_class = VersionManager.dynamic_import_class('ocx', '2.8.6', 'Vessel')
    result = VersionManager.get_meta_data(data_class)
    data_regression.check(result)

def test_dynamic_import_class():
    assert  VersionManager.dynamic_import_class('ocx', '2.8.6', 'Vessel')
