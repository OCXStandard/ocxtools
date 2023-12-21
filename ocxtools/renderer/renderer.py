#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
""" Render classes"""

# System imports
from typing import Dict, List
from pathlib import Path
from enum import Enum
# Third party imports
from tabulate import tabulate
from lxml import etree
from rich.table import Table
from loguru import logger

# Project imports
from ocxtools.utils.utilities import SourceValidator
from ocxtools.exceptions import SourceError
from ocxtools.console.console import style_table_header


class RenderError(ValueError):
    """Render errors."""


class ReportType(Enum):
    """Validator report types"""
    OCX = 'ocx'
    SCHEMATRON = 'schematron'


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


class RichTable:
    """Build a Rich table."""

    @classmethod
    def render(cls, title: str, data: List, show_header: bool = True, caption: str = None):
        """
        Render a rich table
        Args:
            show_header: If True render the table header.
            title: The table title rendered above.
            data: The table content. List of dictionaries where each dictionary
            represents a row in the table, and the keys represent column headers.
            caption: The table caption rendered below.

        Returns:
            The table
        """
        try:
            table = Table(title=title, header_style=style_table_header, caption=caption, show_header=show_header)
            headers = list(data[0].keys())
            for header in headers:
                table.add_column(header)
            for row in data:
                table.add_row(*[str(row[header]) for header in headers])
            return table
        except ValueError as e:
            logger.error(e)
            raise RenderError(e) from e


class XsltTransformer:
    """
        Transform an XML file using an xslt stylesheet.
    """

    def __init__(self, xslt_file: str):
        try:
            self._xslt_file = SourceValidator.validate(xslt_file)
        except SourceError as e:
            raise RenderError(e) from e

    def render(self, data: str, source_file: str, output_folder: str,
               report_type: ReportType = ReportType.SCHEMATRON) -> str:
        """

        Args:
            report_type: The report type. ``OCX`` or ``SCHEMATRON``.
            output_folder: The report folder.
            data: the xml data as a string
            source_file: The source file

        Returns:
            The path to the output file name
        """
        # Parse XML and XSLT files
        file_name = Path(source_file).stem
        output_file = Path(output_folder) / f'{file_name}_{report_type.value}_report.html'
        xml_file = Path(output_folder) / f'{file_name}.xml'
        with xml_file.open('w') as f:
            f.write(data)

        xml_tree = etree.parse(xml_file)
        xslt_tree = etree.parse(self._xslt_file)

        # Create an XSLT processor
        transform = etree.XSLT(xslt_tree)

        # Apply the transformation
        result_tree = transform(xml_tree)

        # Save the result to a new file
        result_tree.write(output_file, pretty_print=True, encoding='utf-8')

        return str(output_file)
