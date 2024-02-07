#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""This module provides the ocx_attribute_reader app functionality."""
# System imports
from pathlib import Path
from typing import Tuple, Any, List, Annotated

# 3rd party imports
import typer
import lxml
import lxml.etree
from rich.table import Table

# Project imports
from ocxtools import config
from ocxtools.renderer.renderer import RichTable
from ocxtools.serializer.serializer import ReportFormat
from ocxtools.exceptions import ReporterError, SourceError
from ocxtools.reporter.reporter import OcxObserver
from ocxtools.reporter.report_manager import OcxReportManager
from ocxtools.reporter.reporter import OcxReportFactory, OcxReporter
from ocxtools.dataclass.dataclasses import ReportType
from ocxtools.context.context_manager import get_context_manager
from ocxtools.reporter import __app_name__
from ocxtools.utils.utilities import SourceValidator
from ocxtools.parser.parser import OcxNotifyParser

report = typer.Typer(help="Reporting of 3Docx attributes")
# Instantiate the singletons
report_manager = OcxReportManager()


@report.command()
def one(
        model: str,
        save: Annotated[
            bool, typer.Option(help="Save a summary report of the validated model in the report folder.")] = False,
        report_format: Annotated[ReportFormat, typer.Option(help="File format")] = ReportFormat.CSV.value,
        report_folder: Annotated[str, typer.Option(help="Path to the report folder")] =
        config.get('ValidatorSettings', 'report_folder'),

):
    """Parse one model for reporting."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    ocx_parser = OcxNotifyParser()
    ocx_reporter = OcxObserver(ocx_parser)
    try:
        file = SourceValidator.validate(model)
        with console.status("Parsing the model..."):
            ocx_parser.parse(file)
            report_manager.add_report(report=ocx_reporter.element_count(model))
            tree = lxml.etree.parse(file)
            root = tree.getroot()
            report_manager.add_report(report=OcxReportFactory.create_header(root, model))
        console.info(f'Successfully parsed {ocx_reporter.get_number_of_elements()} elements in the model: {file!r}')
    except ReporterError as e:
        console.error(f'{e}')
    except SourceError as e:
        console.error(f'{e}')


@report.command()
def delete(
        model: str,

):
    """Delete all reports for a given model."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    count = report_manager.delete_report(model=model)
    console.info(f'Deleted {count} reports for model: {model!r}')


@report.command()
def content(
        model: str,
        ocx_type: Annotated[ReportType, typer.Option(help="Specify the 3Docx content.")] = ReportType.PLATE,
):
    """Create the 3Docx content reports."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    with console.status("Parsing the model for content..."):
        try:

            df = OcxReporter.dataframe(model, ocx_type)
            if df is not None:
                table = Table(show_header=True, header_style="bold magenta", title=ReportType.PLATE.value)
                table = RichTable.df_to_table(df, table, show_index=False)
                console.print_table(table)
            else:
                console.info(f'No OCX elements of type {ocx_type.value} found in model {model!r}.')
        except ReporterError as e:
            console.error(e)


@report.command()
def plates(
        model: str,
):
    """Report ``Plate`` instances."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    with console.status("Parsing the model for plates..."):
        try:
            report = OcxReporter.dataframe(model, ocx_type=ReportType.PLATE)
            report_manager.add_report(report)
            console.info(f'Parsed {report.count} plates.')
        except ReporterError as e:
            console.error(e)


def stiffeners(
        model: str,
):
    """Report ``Stiffener`` instances."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    with console.status("Parsing the model for stiffeners..."):
        try:
            report = OcxReporter.dataframe(model, ocx_type=ReportType.STIFFENER)
            report_manager.add_report(report)
            console.info(f'Parsed {report.count} stiffeners.')
        except ReporterError as e:
            console.error(e)


def brackets(
        model: str,
):
    """Report ``Bracket`` instances."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    with console.status("Parsing the model for stiffeners..."):
        try:
            report = OcxReporter.dataframe(model, ocx_type=ReportType.BRACKET)
            report_manager.add_report(report)
            console.info(f'Parsed {report.count} brackets.')
        except ReporterError as e:
            console.error(e)


@report.command()
def many(
        models: List[Path],
):
    """Parse one model for reporting."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    for model in models:
        if model.is_file():
            one(str(model))
        else:
            console.error(f'Model {str(model.resolve())!r} does not exist.')


@report.command()
def count(
        selection: Annotated[
            str, typer.Option(help="List only selected elements. "
                                   "Give a list of names separated by semicolons ';' and no spaces.")] = 'All'
):
    """Count of OCX types in a 3Docx model."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Element Count')
    if 'All' in selection:
        for elem_count_report in report_manager.get_report(ReportType.ELEMENT_COUNT):
            model = elem_count_report.source
            table = RichTable.render(f'Element count for model {model}', elem_count_report.detail())
            console.print_table(table)
    else:
        for elem_report in report_manager.get_report(ReportType.ELEMENT_COUNT):
            model = elem_report.source
            report = [item for item in elem_report.detail() if item.get('Name') in selection.split(';')]
            table = RichTable.render(f'Element count for model {model}', report)
            console.print_table(table)


@report.command()
def summary():
    """
    3Docx model summary reports
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Report Summary')
    summary = report_manager.report_summary()
    if len(summary) > 0:
        table = RichTable.render(data=summary, title='Summary')
        console.print_table(table)
    else:
        console.info('There are no reports available')


@report.command()
def headers():
    """
    3Docx model headers reports
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Report Headers')
    summary = report_manager.report_headers()
    table = RichTable.render(data=summary, title='Headers')
    console.print_table(table)


@report.command()
def details(report_type: ReportType = ReportType.ELEMENT_COUNT.value):
    """
    3Docx model detailed reports
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Report Details')
    for data in report_manager.report_detail(report_type):
        if data is not None:
            table = (RichTable.render(data=data, title=report_type.value))
            console.print_table(table)
        else:
            console.info(f'There are no detailed reports for report {report_type.value!r}')


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(report)
    return __app_name__, typer_click_object
