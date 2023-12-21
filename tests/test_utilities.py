#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from collections import defaultdict

from ocxtools.utils import utilities


def test_filter_files(shared_datadir, data_regression):
    result = {file.name: file.name for file in utilities.SourceValidator.filter_files(str(shared_datadir), '*.3docx')}
    data_regression.check(result)


def test_is_url():
    assert utilities.SourceValidator.is_url("file://models/m1.3docx")


def test_is_directory(shared_datadir):
    assert utilities.SourceValidator.is_directory(str(shared_datadir))


TEST_DICT = {
    "Bob": "male",
    "Jenny": "female",
    "Axel": "boy",
    "Eva": "girl",
    "Theodora": "hen",
}

DEFAULTDICT = defaultdict(list)
DEFAULTDICT["col1"].append(range(6))
DEFAULTDICT["col2"].append((range(5, 10)))


def test_number_table_rows(data_regression):
    numbered_dict = utilities.number_table_rows(TEST_DICT)
    index = [0, 1, 2, 3]
    assert index == numbered_dict["#"]


def test_camel_case_split():
    camel_case = "pythonGeekForGeeks"
    words = utilities.camel_case_split(camel_case)
    assert words == ["Geek", "For", "Geeks"]


def test_dromedary_case_split():
    camel_case = "pythonGeekForGeeks"
    words = utilities.dromedary_case_split(camel_case)
    assert words == ["python", "Geek", "For", "Geeks"]
