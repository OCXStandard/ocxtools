#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""This module provides the ocx_attribute_reader app functionality."""
# System imports
from typing import Annotated, Any, Tuple

# 3rd party imports
import typer

# Project imports
from ocxtools import config
from ocxtools.context.context_manager import get_context_manager
from ocxtools.dataclass.dataclasses import ReportType
from ocxtools.exceptions import ReporterError
from ocxtools.rds import __app_name__
from ocxtools.renderer.renderer import RichTable
from ocxtools.reporter.report_manager import OcxReportManager
from ocxtools.reporter.reporter import OcxReporter
from ocxtools.serializer.serializer import (ReportFormat, Serializer,
                                            SerializerError)
from ocxtools.utils.utilities import SourceError, SourceValidator

rds = typer.Typer(help="Reference Designation System output.")
report_manager = OcxReportManager()  # Singleton
REPORT_FOLDER = SourceValidator.mkdir(config.get('ValidatorSettings', 'report_folder'))


@rds.command()
def delete(
        model: str,

):
    """Delete all reports for a given model."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    count = report_manager.delete_report(model=model)
    console.info(f'Deleted {count} reports for model: {model!r}')


@rds.command()
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
    try:
        SourceValidator.validate(model)
        match report_type:
            case ReportType.ALL.value:
                with console.status("Parsing the model content for all elements...") as status:
                    for member_name, member_value in ReportType.__members__.items():
                        if member_value.value not in [ReportType.ALL.value, ReportType.COUNT.value]:
                            status.update(f'Parsing {member_value.value}')
                            try:
                                report = OcxReporter.dataframe(model, member_value)
                                if report is not None:
                                    report_manager.add_report(report)
                                    if save and report_format.value == ReportFormat.PARQUET.value:
                                        Serializer.serialize_to_parquet(report=report, report_folder=report_folder)
                                        status.update(f'Saving report for {member_value.value}')
                            # Catch a parser error, log a message but continue
                            except (ReporterError, SerializerError) as e:
                                console.error(f'An error occurred while parsing {member_value.value}')
                                console.error(str(e))
                                console.error(f'Further parsing og {member_value.value} is skipped.')
            case ReportType.COUNT.value:
                with console.status(f"Parsing the model for content {report_type.value}...") as status:
                    report = OcxReporter.dataframe(model, report_type)
                    if report is not None:
                        report_manager.add_report(report)
                        if save:
                            Serializer.serialize_to_parquet(report=report, report_folder=REPORT_FOLDER)
                            status.update(f'Saving report for {report_type.value}')
            case _:
                with console.status(f"Parsing the model for content {report_type.value}...") as status:
                    status.update(f'Parsing {report_type.value}')
                    try:
                        report = OcxReporter.dataframe(model, report_type)
                        if report is not None:
                            report_manager.add_report(report)
                            if save and report_format.value == ReportFormat.PARQUET.value:
                                Serializer.serialize_to_parquet(report=report, report_folder=report_folder)
                                status.update(f'Saving report for {report_type.value}')
                    # Catch a parser error, log a message but continue
                    except (ReporterError, SerializerError) as e:
                        console.error(f'An error occurred while parsing {report_type.value}')
                        console.error(str(e))
                        console.error(f'Further parsing og {report_type.value} is skipped.')

        summary()
    except SourceError as e:
        console.error(str(e))



@rds.command()
def summary():
    """
    3Docx model summary reports
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
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


@rds.command()
def details(
        report: Annotated[
            ReportType, typer.Option(help="Specify the 3Docx content.")] = ReportType.PARTICULARS.value,
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
    try:
        to_col = int(max_col)
        console.section('Report Details')
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


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(rds)
    return __app_name__, typer_click_object
