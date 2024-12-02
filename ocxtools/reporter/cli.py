#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""This module provides the ocx_attribute_reader app functionality."""
# System imports
from pathlib import Path
from typing import Annotated, Any, List, Tuple, Union

# 3rd party imports
import typer

from ocxtools import config
from ocxtools.console.console import CliConsole
from ocxtools.context.context_manager import get_context_manager
from ocxtools.dataclass.dataclasses import Report, ReportDataFrame, ReportType
from ocxtools.exceptions import ReporterError
from ocxtools.renderer.renderer import RichTable
# Project imports
from ocxtools.reporter import __app_name__
from ocxtools.reporter.reporter import OcxReporter
from ocxtools.serializer.serializer import (ReportFormat, Serializer,
                                            SerializerError)
from ocxtools.utils.utilities import SourceError, SourceValidator

report = typer.Typer(help="Reporting of 3Docx attributes")
REPORT_FOLDER = SourceValidator.mkdir(config.get('ValidatorSettings', 'report_folder'))


def parse_content(console: CliConsole, status, model: str, report_type: ReportType) -> Union[Report, None]:
    """
    Parses the content of a given model and report type.

    Args:
        status: The Cli.Console.satus method
        console: The CLI console object.
        model: The model to parse.
        report_type: The type of report to generate.

    Returns:
        Union[Report, None]: The parsed report if successful, None otherwise.

    Raises:
        ReporterError: If an error occurs during parsing.
        SerializerError: If an error occurs during serialization.

    Examples:
        # Example usage of parse_content function
        console = CliConsole()
        model = "example_model"
        report_type = ReportType.VESSEL
        result = parse_content(console, model, report_type)
    """
    status.update(f'Parsing {report_type.value}')
    try:
        return OcxReporter.dataframe(model, report_type)
    except (ReporterError, SerializerError) as e:
        console.error(f'An error occurred while parsing {report_type.value}')
        console.error(str(e))
        console.error(f'Further parsing of {report_type.value} is skipped.')


def serialize_content(report: ReportDataFrame, status, report_folder: str, report_format: ReportFormat,
                      save: bool = True):
    """
    Serializes the content of a report to a specified format and saves it to a folder.

    Args:
        report: The report to serialize.
        status: The status object.
        report_folder: The folder to save the serialized report.
        report_format: The format in which to serialize the report.
        save: Optional. Indicates whether to save the serialized report. Defaults to True.

    Returns:
        None

    Examples:
        # Example usage of serialize_content function
        report = ReportDataFrame(...)
        status = Status(...)
        report_folder = "reports"
        report_format = ReportFormat.PARQUET
        serialize_content(report, status, report_folder, report_format, save=True)
    """
    if save and report_format.value == ReportFormat.PARQUET.value:
        Serializer.serialize_to_parquet(report=report, report_folder=report_folder)
        status.update(f'Saving report for {report.type.value}')


@report.command()
def delete(
        model: str,

):
    """Delete all reports for a given model."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    report_manager = context_manager.get_report_manager()
    count = report_manager.delete_report(model=model)
    console.info(f'Deleted {count} reports for model: {model!r}')


@report.command()
def content(
        model: str,
        report_type: Annotated[ReportType, typer.Option(
            help="Create the report type. All will create all reports")] = ReportType.VESSEL.value,
        save: Annotated[
            bool, typer.Option(help="Save a detailed report of the validated models in the report folder.")] = True,
        report_format: Annotated[ReportFormat, typer.Option(help="File format")] = ReportFormat.PARQUET.value,
        report_folder: Annotated[str, typer.Option(help="Path to the report folder")] = REPORT_FOLDER,
):
    """Create the 3Docx content reports."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    report_manager = context_manager.get_report_manager()
    try:
        SourceValidator.validate(model)
        match report_type.value:
            case ReportType.ALL.value:
                with console.status("Parsing the model content for all elements...") as status:
                    for member_name, member_value in ReportType.__members__.items():
                        if member_value.value not in [ReportType.ALL.value, ReportType.COUNT.value]:
                            report = parse_content(console=console, status=status, model=model,
                                                   report_type=member_value)
                            if report is not None:
                                report_manager.add_report(report)
                                serialize_content(report=report, status=status, report_folder=report_folder,
                                                  report_format=ReportFormat.PARQUET)
            case ReportType.COUNT.value:
                with console.status(f"Parsing the model for content {report_type.value}...") as status:
                    report = parse_content(console=console, status=status, model=model,
                                           report_type=report_type)
                    if report is not None:
                        report_manager.add_report(report)
                        serialize_content(report=report, status=status, report_folder=report_folder,
                                          report_format=ReportFormat.PARQUET)
            case _:
                with console.status(f"Parsing the model for content {report_type.value}...") as status:
                    report = parse_content(console=console, status=status, model=model,
                                           report_type=report_type)
                    if report is not None:
                        report_manager.add_report(report)
                        serialize_content(report=report, status=status, report_folder=report_folder,
                                          report_format=ReportFormat.PARQUET)
        summary()
    except SourceError as e:
        console.error(str(e))


@report.command()
def many(
        models: List[Path],
):
    """Parse one model for reporting."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    for model in models:
        if model.is_file():
            content(model=str(model), ocx_type=ReportType.ALL)
        else:
            console.error(f'Model {str(model.resolve())!r} does not exist.')


@report.command()
def count(
        model: str,
):
    """
    3Docx model count elements report
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    report_manager = context_manager.get_report_manager()
    try:
        with console.status("Counting elements in the model..."):
            reporter = OcxReporter()
            reporter.parse_model(model)
            report = reporter.element_count()
            if report is not None:
                report_manager.add_report(report)
                console.info(f'Parsed {report.count} elements')
        summary()
    except ReporterError as e:
        console.error(str(e))


@report.command()
def summary():
    """
    3Docx model summary reports
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    report_manager = context_manager.get_report_manager()
    console.section('Report Summary')
    try:
        summary = report_manager.report_summary()
        if len(summary) > 0:
            table = RichTable.render(data=summary, title='Summary')
            console.print_table(table)
        else:
            console.info('There are no reports available')
    except ReporterError as e:
        console.error(str(e))


@report.command()
def details(
        report: Annotated[
            ReportType, typer.Option(help="Specify the 3Docx content.")] = ReportType.VESSEL.value,
        level: Annotated[int, typer.Option(help="Display table data including level No. "
                                                "The default is to display only data at level zero.")] = 0,
        max_col: Annotated[str, typer.Option(help="Number of columns to display."
                                                  " The default is to display 8 columns")] = '8',
        member: Annotated[str, typer.Option(help="Show only details for the OCX member.")] = 'All',
        guid: Annotated[str, typer.Option(help="Show only details for the OCX member with guid.")] = ''

):
    """
    3Docx model detailed reports.
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    report_manager = context_manager.get_report_manager()
    try:
        to_col = int(max_col)
        console.section('Report Details')
        if report_manager.has_report(report.value):
            for item in report_manager.report_detail(report_type=report,
                                                     level=level,
                                                     max_col=to_col,
                                                     member=member,
                                                     guid=guid):
                if item is not None:
                    if guid != '':
                        title = (f'Source: {item.source}. Columns: {item.columns}, Levels: {item.levels}, '
                                 f'Current level: {level}, Member: {member!r}, GUIDref={guid!r}')
                    else:
                        title = (f'Source: {item.source}. Columns: {item.columns}, Levels: {item.levels}, '
                                 f'Current level: {level}, Member: {member!r}')
                    table = (RichTable.render(data=item.content, title=title))
                    console.print_table(table)
        else:
            console.info(f'There are no detailed reports for report {report.value!r}')
    except ReporterError as e:
        console.error(str(e))


@report.command()
def tree(
        report: Annotated[
            ReportType, typer.Option(help="Specify the 3Docx report.")] = ReportType.VESSEL.value,
):
    """
    3Docx content table levels.
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    report_manager = context_manager.get_report_manager()
    try:
        console.section('Table Tree')
        for item in report_manager.report_tree(report_type=report):
            if item is not None:
                table = RichTable.render(data=[item], title=report.value)
                console.print_table(table)
            else:
                console.info(f'There are no detailed reports for report {report.value!r}')
    except ReporterError as e:
        console.error(str(e))


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(report)
    return __app_name__, typer_click_object
