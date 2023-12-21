#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Provide context information between sub-commands."""

# System imports
from typing import Union, Dict
# Third party imports
import click
from configparser import ConfigParser
# Project
from ocxtools.console.console import CliConsole
from ocxtools.validator.validator_report import ValidationReport
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

    def add_report(self, domain: ValidationDomain, report: ValidationReport):
        """
            Add a new source model and report html file
        Args:
            domain: The validation domain
            source: The path to the source model
            report: The validation report

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
