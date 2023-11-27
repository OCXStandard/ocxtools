#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Shared utility classes and functions"""
# System imports
from itertools import groupby
from pathlib import Path
from urllib.parse import urlparse


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
                raise ValueError(f"(The {source} is not a valid url.")
        # File
        else:
            file_path = Path(source)
            if file_path.exists():
                return str(file_path.resolve())
            else:
                raise ValueError(f"The {source} does not exist.")


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
                version = item[item.find("=") + 2 : -1]
        return version


class OcxNamespace:
    """Find the schema namespace of the 3Docx XML model."""

    @staticmethod
    def ocx_namespace(model: str) -> str:
        """Return the OCX schema namespace of the model.

        Args:
            model: The sorce path or uri

        Returns:
              The OCX schema namespace of the model.
        """
        namespace = "NA"
        ocx_model = Path(model).resolve()
        content = ocx_model.read_text().split()
        for item in content:
            if "xmlns:ocx" in item:
                namespace = item[item.find("=") + 2 : -1]
        return namespace
