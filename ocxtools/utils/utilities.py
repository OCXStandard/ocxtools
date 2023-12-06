#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Shared utility classes and functions"""
# System imports
from itertools import groupby
from pathlib import Path
from urllib.parse import urlparse
from typing import Generator

# Project imports
from ocxtools.exceptions import SourceError


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
        version = "NA"
        ocx_model = Path(model).resolve()
        content = ocx_model.read_text().split()
        for item in content:
            if "schemaVersion" in item:
                version = item[item.find("=") + 2: -1]
        return version


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
