#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Shared utility classes and functions"""
# System imports
import errno
import logging
import os
import re
import sys
from collections import defaultdict
from itertools import groupby
from pathlib import Path
from typing import Dict, Generator, List
from urllib.parse import urlparse

import yaml

# Project imports
from ocxtools.exceptions import SourceError


def is_substring_in_list(substring, string_list):
    """

    Args:
        substring: The search string
        string_list: List of strings

    Returns:
        True if the substring is found, False otherwise.
    """
    return any(substring in string for string in string_list)


def all_equal(iterable) -> True:
    """
    Verify that all items in a list are equal
    Args:
        iterable:

    Returns:
        True if all are equal, False otherwise.
    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def root_dir() -> str:
    """Path to the directory of the parent module."""
    return os.path.realpath(os.path.join(os.path.dirname(__file__), "../../"))


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def current_dir(file: str) -> str:
    """The full path to the folder containing the ``file``

    Args:
        file: The name of an existing file
    """
    return os.path.realpath(os.path.join(os.path.dirname(file), ""))


def nested_dict():
    """
    A recursive function that creates a default dictionary where each value is
    another default dictionary.
    """
    return defaultdict(nested_dict)


def default_to_regular(d) -> Dict:
    """
    Converts defaultdicts of defaultdicts to dict of dicts.

    Args:
        d: The dict to be converted

    """
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def default_to_grid(d) -> Dict:
    """
    Converts defaultdicts to a data grid with unique row ids.

    Args:
        d: The dict to be converted

    """
    if isinstance(d, defaultdict):
        print(d.items())
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def get_path_dict(paths):
    new_path_dict = nested_dict()
    for path in paths:
        if parts := path.split("/"):
            marcher = new_path_dict
            for key in parts[:-1]:
                marcher = marcher[key]
            marcher[parts[-1]] = parts[-1]
    return default_to_regular(new_path_dict)


# Components for pretty print a directory tree structure
# prefix components:
space = "    "
branch = "│   "
# pointers:
tee = "├── "
last = "└── "


def tree(paths: dict, prefix: str = ""):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(paths) - 1) + [last]
    for pointer, path in zip(pointers, paths):
        yield prefix + pointer + path
        if isinstance(paths[path], dict):  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(paths[path], prefix=prefix + extension)


def number_table_rows(table: dict, first_index: int = 0) -> Dict:
    """Utility function to add row numbers to the first column of a table stored as a dict.

    Args:
        table: The input table dict
        first_index: The first row index value. Default = 0

    Returns:
        a table (dict) with numbered rows in the first column

    """
    size = len(list(table.values())[0])
    tbl = defaultdict(list)
    for i in range(first_index, size + first_index):
        tbl["#"].append(i)
    tbl |= table
    return tbl


def find_replace_multi(string, dictionary) -> str:
    """Substitute every value in a dict if it matches."""
    for item in dictionary.keys():
        # sub item for item's paired value in string
        string = re.sub(item, dictionary[item], string)
    return string


def logging_level(loglevel: str) -> int:
    """Utility function to return the logging level.

    Args:
        loglevel: One of ``INFO``, ``WARNING``, ``ERROR`` or ``DEBUG``
    """
    # Set the console logging level
    level = logging.INFO
    if loglevel == "ERROR":
        level = logging.ERROR
    elif loglevel == "WARNING":
        level = logging.WARNING
    elif loglevel == "DEBUG":
        level = logging.DEBUG
    return level


def list_files_in_directory(directory: str, file_ext: str = ".3docx") -> list:
    """Utility function to list files in a directory.

    Args:
        directory: the name of the directory.
        file_ext: Only files with matching extension will be listed.
    Returns:
       list of matching files.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise AssertionError(errno.EEXIST)
    return [
        x.name
        for x in sorted(dir_path.iterdir())
        if x.is_file() and x.suffix.lower() == file_ext
    ]


def load_yaml_config(config: str) -> dict:
    """Safely read a yaml config file and return the content as a dict.

    Args:
        config: Path to yaml file
    Raises:
        Raise ``errno.ENOENT`` if yaml file does not exist
    """
    resource_file = resource_path(config)
    if not Path(resource_file).exists():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), resource_file)
    with open(resource_file) as f:
        app_config = yaml.safe_load(f)
    return app_config


def camel_case_split(str) -> List:
    """Split camel case string to individual strings."""
    return re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", str)


def dromedary_case_split(str) -> List:
    """Split camel case string to individual strings."""
    return re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", str)


def get_file_path(file_name):
    """Get the correct file path also when called within a one-file executable."""
    base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath(".")
    return os.path.join(base_path, file_name)


class SourceValidator:
    """Methods for validating the existence of a data source."""

    @staticmethod
    def validate(source: str) -> str:
        """
        Validate the existence of a data source.

        Args:
            source: The source file path or url.

        Returns:
            Returns the uri or full path if the source is valid.
        Raises:
              Raises a ValueError if source is invalid
        """
        # Url
        if "http" in source:
            parsed_url = urlparse(source)
            if bool(parsed_url.scheme and parsed_url.netloc):
                return parsed_url.geturl()
            else:
                raise SourceError(f"(The {source} is not a valid url.")
        # File
        else:
            file_path = Path(source)
            if file_path.exists():
                return str(file_path.resolve())
            else:

                raise SourceError(f"The {source} does not exist.")

    @staticmethod
    def is_url(source: str) -> bool:
        """Return true if ``source`` is a valid url."""
        parsed_url = urlparse(source)
        return bool(parsed_url.scheme and parsed_url.netloc)

    @staticmethod
    def is_directory(source: str) -> bool:
        """Return True if the source is a directory, False otherwise"""
        return Path(source).is_dir()

    @staticmethod
    def mkdir(source: str) -> str:
        """Create the directory and any parent folders if missing.

        Args:
            source: The folder name

        Returns:
            The folder name
        """
        folder = Path(source)
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        return source

    @staticmethod
    def filter_files(directory: str, filter_str: str) -> Generator:
        """Return an iterator over the filtered files in the ``directory``."""
        if SourceValidator.is_directory(directory):
            # Specify the folder path
            folder_path = Path(directory)
            # Using glob to filter files based on a pattern
            return folder_path.glob(filter_str)


class OcxVersion:
    """Find the schema version of an 3Docx XML model."""

    @staticmethod
    def get_version(model: str) -> str:
        """
        The schema version of the model.
        Args:
            model: The source file path or uri

        Returns:
            The schema version of the 3Docx XML model.
        """
        try:
            version = "NA"
            ocx_model = Path(SourceValidator.validate(model))
            content = ocx_model.read_text().split()
            for item in content:
                if "schemaVersion" in item:
                    version = item[item.find("=") + 2: -1]
            return version
        except SourceError as e:
            raise SourceError(e) from e


class OcxNamespace:
    """Find the schema namespace of the 3Docx XML model."""

    @staticmethod
    def ocx_namespace(model: str) -> str:
        """Return the OCX schema namespace of the model.

        Args:
            model: The source path or uri

        Returns:
              The OCX schema namespace of the model.
        """
        namespace = "NA"
        ocx_model = Path(model).resolve()
        content = ocx_model.read_text().split()
        for item in content:
            if "xmlns:ocx" in item:
                namespace = item[item.find("=") + 2: -1]
        return namespace
