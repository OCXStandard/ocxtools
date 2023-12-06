#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Provide context information between sub-commands."""

# System imports
from typing import List


class ContextManager:
    """
        Provide context between sub commands.
    """

    def __init__(self):
        self._ocx_reports: List = []
        self._schematron_reports: List = []

    def add_ocx_report(self, source: str, report_file: str):
        """
            Add a new source model and report html file
        Args:
            source: The path to the source model
            report_file: The validation report
        """
        self._ocx_reports.append({source: report_file})

    def add_schematron_report(self, source: str, report_file: str):
        """
            Add a new source model and report html file
        Args:
            source: The source model
            report_file: The validation report
        """
        self._ocx_reports.append({source: report_file})

    def get_ocx_reports(self) -> List:
        """
            List of OCX validation reports
        Returns:
            List of reports
        """
        return self._ocx_reports

    def get_schematron_reports(self) -> List:
        """
            List of Schematron validation reports
        Returns:
            List of reports
        """
        return self._schematron_reports
