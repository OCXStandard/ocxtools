#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""This module provides the ocx_attribute_reader app functionality."""
# System imports
from pathlib import Path
from typing import Tuple, Any, List, Annotated
# 3rd party imports
import typer
# Project imports
from ocxtools import config
from ocxtools.renderer.renderer import RichTable
from ocxtools.serializer.serializer import ReportFormat
from ocxtools.exceptions import ReporterError, SourceError
from ocxtools.reporter.reporter import OcxReporter
from ocxtools.reporter.report_manager import OcxReportManager
from ocxtools.context.context_manager import get_context_manager
from ocxtools.reporter import __app_name__
from ocxtools.utils.utilities import SourceValidator

report = typer.Typer(help="Reporting of 3Docx attributes")
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
    try:
        file = SourceValidator.validate(model)
        with console.status("Parsing the model..."):
            reporter = OcxReporter(model)
            header = reporter.parse_model()
            report_manager.add_report(model=str(model), report=header)
        console.info(f'Successfully parsed model: {file!r}')
        # Create the reports
        with console.status("Creating the reports..."):
            report_manager.add_report(model=str(model), report=reporter.check_references())
            report_manager.add_report(report=reporter.check_duplicates(), model=str(model))
        console.info(f'Created reports for model: {model!r}')
    except ReporterError as e:
        console.error(f'{e}')
    except SourceError as e:
        console.error(f'{e}')


@report.command()
def many(
        models: List[Path],
):
    """Parse one model for reporting."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    for model in models:
        if model.is_file():
            one(model)
        else:
            console.error(f'Model {str(model.resolve())!r} does not exist.')


# @report.command()
# def count(
# ):
#     """Count of OCX types in a 3Docx model."""
#     context_manager = get_context_manager()
#     console = context_manager.get_console()
#     selection = typer.prompt("Select the OCX entities as a list of names (blank space as separator). "
#                              "Enter 'All' to count all the objects in the model", type=str)
#     if selection.lower() == "all":
#         selection = ["All"]
#     else:
#         selection = selection.split()
#         if not typer.confirm(f'You entered: {selection}'):
#             return
#     element_count = reporter.element_count(selection=selection)
#     table = RichTable.render('Element Count', element_count)
#     console.print_table(table)


@report.command()
def duplicates(
):
    """Detailed duplicate guids reports for all parsed models."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    duplicates = context_manager.get_duplicate_guids_reports()
    console.section('Duplicate GUIDs')
    for model in duplicates:
        tables = RichTable.render(f'Duplicates in model {model}',
                                  [table.to_dict(exclude='Model') for table in duplicates[model]])
        console.print_table(tables)


@report.command()
def missing(model: str):
    """Report 3Docx elements with missing references."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Missing References')
    reports = report_manager.get_report(model)
    for report in reports:
        context_manager.add_missing_guids_report()
        tables = RichTable.render(f'Missing references in model {missing[0].model}',
                                  [table.to_dict(exclude='MissingGuids') for table in missing])
        console.print_table(tables)
    else:
        console.info(f'No missing references in model {model}')


@report.command()
def summary():
    """
    3Docx model summary reports
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Report Summary')
    summary = report_manager.report_summary()
    table = RichTable.render(data=summary, title='Summary')
    console.print_table(table)


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
def details(model: str):
    """
    3Docx model detailed reports
    """
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Report Details')
    if tables := [
        report
        for report in report_manager.report_detail(model)
        if report is not None
    ]:
        table = (RichTable.render(data=tables, title=model))
        console.print_table(table)
    else:
        console.info(f'There are no detailed reports for model {model!r}')


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(report)
    return __app_name__, typer_click_object
