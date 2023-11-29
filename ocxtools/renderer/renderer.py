#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
""" Render classes"""

# System imports
from typing import Dict

# Third party imports
from tabulate import tabulate
from lxml import etree

# Project imports
from ocxtools.utils.utilities import SourceValidator
from ocxtools.exceptions import SourceError, RenderError


class TableRender:
    @staticmethod
    def render(data: Dict):
        """

        Args:
            data:

        Returns:

        """
        headers = []
        values = []
        for k, v in data.items():
            headers.append(k)
            values.append(v)
        return tabulate([headers, values], headers="firstrow")


class XsltTransformer:
    """
        Transform an XML file using an xslt stylesheet.
    """

    def __init__(self, xslt_file: str):
        try:
            self._xslt_file = SourceValidator.validate(xslt_file)
        except SourceError as e:
            raise RenderError(e) from e

    def render(self, data: bytes,  output_file: str):
        """

        Args:
            data: the xml data as a byte string
            output_file: The output file
        """
        # Parse XML and XSLT files
        xml_tree = etree.fromstring(data)
        xslt_tree = etree.parse(self._xslt_file)

        # Create an XSLT processor
        transform = etree.XSLT(xslt_tree)

        # Apply the transformation
        result_tree = transform(xml_tree)

        # Save the result to a new file
        result_tree.write(output_file, pretty_print=True, encoding='utf-8')
