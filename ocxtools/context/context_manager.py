#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Provide context information between sub-commands."""

from configparser import ConfigParser
# System imports
from typing import Dict, Union

# Third party imports
import click

# Project
from ocxtools.console.console import CliConsole
from ocxtools.dataclass.dataclasses import OcxHeader, ValidationReport
from ocxtools.reporter.report_manager import OcxReportManager
from ocxtools.validator.validator_client import ValidationDomain


class ContextManager:
    """
    Provide context between sub commands.

    Args:
        console: The main CLI console
        config: The app configuration

    """

    def __init__(self, console: CliConsole, config: ConfigParser):
        self._ocx_reports: Dict = {}
        self._schematron_reports: Dict = {}
        self._console = console
        self._config = config
        self._headers: Dict = {}
        self._report_manager = OcxReportManager()

    def add_header(self, header: OcxHeader):
        """
            Add the 3Docx header information.
        Args:
            header: The header dataclass

        """

        self._headers[header.source] = header

    def get_headers(self) -> Dict:
        """Return 3Docx header information."""
        return self._headers

    def add_report(self, domain: ValidationDomain, report: ValidationReport):
        """
            Add a new source model and report dataclass
        Args:
            domain: The validation domain
            report: The validation report dataclass

        """
        match domain:
            case ValidationDomain.OCX:
                self._ocx_reports[report.source] = report
            case _:
                self._schematron_reports[report.source] = report

    def get_report(self, model: str) -> Union[ValidationReport, None]:
        """
            Get the report for the ``model``.
        Returns:
            The validation report, None list of none

        """
        if model in self._ocx_reports:
            return self._ocx_reports.get(model)
        else:
            return self._schematron_reports.get(model)

    def get_report_manager(self) -> OcxReportManager:
        """
        Returns the OcxReportManager instance associated with the context manager.

        Returns:
            OcxReportManager: The OcxReportManager instance associated with the context manager.
        """
        return self._report_manager

    def get_ocx_reports(self) -> Dict:
        """
            List of OCX validation reports
        Returns:
            List of reports

        """
        return self._ocx_reports

    def get_schematron_reports(self) -> Dict:
        """
            List of Schematron validation reports
        Returns:
            List of reports

        """
        return self._schematron_reports

    def get_console(self) -> CliConsole:
        """
        The CLI Console.
        Returns:
            Return the Console singleton.

        """
        return self._console

    def get_config(self):
        """Return the app configuration"""
        return self._config


def get_context_manager() -> ContextManager:
    """
    Return the singleton context manager.

    Returns:
    The app context manager.

    """
    ctx = click.get_current_context()
    return ctx.obj
