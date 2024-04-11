#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Validator CLI."""
# System imports
import base64
import json
from pathlib import Path
from typing import Any, List, Tuple

import click
import typer
# 3rd party imports
from loguru import logger
from typing_extensions import Annotated

# Project imports
from ocxtools import config
from ocxtools.context.context_manager import get_context_manager
from ocxtools.renderer.renderer import RichTable
from ocxtools.serializer.serializer import ReportFormat, Serializer
from ocxtools.utils.utilities import SourceValidator
from ocxtools.validator import __app_name__
from ocxtools.validator.validator_client import (EmbeddingMethod,
                                                 OcxValidatorClient,
                                                 ValidationDomain,
                                                 ValidatorError)
from ocxtools.validator.validator_report import ValidatorReportFactory

REPORT_FOLDER = SourceValidator.mkdir(config.get('ValidatorSettings', 'report_folder'))
SUFFIX = config.get('ValidatorSettings', 'report_suffix')
VALIDATOR = config.get('ValidatorSettings', 'validator_url')
validate = typer.Typer(help="Validation of 3Docx models.")


@validate.command()
def one(
        model: str,
        domain: Annotated[ValidationDomain, typer.Option(help="The validator domain.")] = ValidationDomain.OCX.value,
        schema_version: Annotated[str, typer.Option(help="Input schema version.")] = "3.0.0",
        embedding: Annotated[
            EmbeddingMethod, typer.Option(help="The embedding method.")
        ] = EmbeddingMethod.BASE64.value,
        force: Annotated[bool, typer.Option(help="Validate against the input schema version.")] = False,
        save: Annotated[
            bool, typer.Option(help="Save a detailed report of the validated model in the report folder.")] = False,
        report_folder: Annotated[str, typer.Option(help="Path to the report folder")] = REPORT_FOLDER,
):
    """Validate one 3Docx XML file with the docker validator."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    try:
        with console.status("Waiting for the validator to finish..."):
            client = OcxValidatorClient(VALIDATOR)
            response, header = client.validate_one(
                ocx_model=model, domain=domain, schema_version=schema_version,
                embedding_method=embedding, force_version=force
            )
        console.section('Validate One')
        report_data = ValidatorReportFactory.create_report(model, response, header)
        table = report_data.to_dict(exclude=['Report', 'Errors', 'Warnings', 'Assertions', 'OCX Header'])
        logger.info(f'Validated model {model} with result: {report_data.result}. '
                    f'Errors: {report_data.errors} '
                    f'Warnings: {report_data.warnings} '
                    f'Assertions: {report_data.assertions}')
        context_manager.add_report(domain=domain, report=report_data)
        console.info(f'Created validation report for model {model!r}')
        match report_data.result:
            case 'SUCCESS':
                console.info(report_data.result)
            case _:
                console.error(report_data.result)
        summary_table = RichTable.render('Validation results', [table])
        if save:
            details(save=True, report_format=ReportFormat.CSV, report_folder=report_folder),
        else:
            console.print_table(summary_table)
    except ValidatorError as e:
        console.error(f'{e}')


@validate.command()
def gui(
        domain: Annotated[ValidationDomain, typer.Option(help="The validator domain.")] = ValidationDomain.OCX.value,
):
    """Use the docker GUI to validate a 3Docx model."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    url = f'{VALIDATOR}/{domain.value}/upload'
    console.html_page(url)


@validate.command()
def many(
        models: List[str],
        filter: Annotated[str, typer.Option(help="Filter models to validate.")] = "*.3docx",
        domain: Annotated[ValidationDomain, typer.Option(help="The validator domain.")] = ValidationDomain.OCX.value,
        schema_version: Annotated[str, typer.Option(help="Input schema version.")] = "3.0.0",
        embedding: Annotated[
            EmbeddingMethod, typer.Option(help="The embedding method.")
        ] = "BASE64",
        force: Annotated[bool, typer.Option(help="Validate against the input schema version.")] = False,
        save: Annotated[bool, typer.Option(help="Save a summary report of the validated models in the report folder.")]
        = False,
        report_folder: Annotated[str, typer.Option(help="Path to the report folder")] = REPORT_FOLDER,
):
    """Validate many 3Docx XML files with the docker validator."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    selected_files = []
    if len(models) == 1 and Path(models[0]).is_dir():
        files = [model.resolve() for model in SourceValidator.filter_files((models[0]), filter)]
        selection = typer.prompt(f'Select models (give a list of indexes, separated by spaces): '
                                 f'{[(files.index(file), file.name) for file in files]}?')
        selected_files = [str(files[int(indx)]) for indx in selection.split()]
        if typer.confirm(f'Selected files: {selected_files}'):
            console.section('Validate Many')
        else:
            return
    else:
        for model in models:
            if Path(model).exists():
                selected_files.append(model)
            else:
                console.error(f'model {model} does not exist')
    tables = []
    console.info(f'Selected files: {selected_files}')
    try:
        with console.status("Waiting for the validator to finish..."):
            client = OcxValidatorClient(VALIDATOR)
            responses, ocx_headers = client.validate_many(
                ocx_models=selected_files,
                domain=domain, schema_version=schema_version,
                embedding_method=embedding, force_version=force
            )
        for indx, response in enumerate(json.loads(responses)):
            header = ocx_headers[indx]
            encoded_report = response.get('report')
            decoded_bytes = base64.b64decode(encoded_report)
            report = decoded_bytes.decode('utf-8')
            report_data = ValidatorReportFactory.create_report(selected_files[indx], report, header)
            logger.info(f'Validated model {selected_files[indx]} with result: {report_data.result}. '
                        f'Errors: {report_data.errors} '
                        f'Warnings: {report_data.warnings} '
                        f'Assertions: {report_data.assertions}')
            tables.append(report_data.to_dict(exclude=['Report', 'Errors', 'Warnings', 'Assertions', 'OCX Header']))
            ctx = click.get_current_context()
            context_manager = ctx.obj
            context_manager.add_report(domain=domain, report=report_data)
            console.info(f'Created validation report for model {str(selected_files[indx])!r}')
    except ValidatorError as e:
        console.error(f'{e}')
    summary_table = RichTable.render('Validation results', tables)
    if save:
        summary(save=True, report_format=ReportFormat.CSV, report_folder=report_folder),
    else:
        console.print_table(summary_table)


# @typer_async
@validate.command()
def info():
    """Verify that the Docker validator is alive and obtain the available validation options."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Validator Information')
    try:
        with OcxValidatorClient(VALIDATOR) as client:
            response = client.get_validator_info()
        reporter = ValidatorReportFactory()
        information = reporter.create_info_report(response)
        data = [item.to_dict() for item in information]
        table = RichTable.render(title=f'Validator server: {VALIDATOR}',
                                 data=data, caption='The validation domains and supported schema versions'
                                 )
        console.print_table(table)
    except ValidatorError as e:
        console.error(f'{e}')


@validate.command()
def summary(
        save: Annotated[
            bool, typer.Option(help="Save a summary report of the validated model in the report folder.")] = False,
        report_format: Annotated[ReportFormat, typer.Option(help="File format")] = ReportFormat.CSV.value,
        report_folder: Annotated[str, typer.Option(help="Path to the report folder")] = REPORT_FOLDER,
):
    """List validation summary results."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Validation Summary')
    validated = list(context_manager.get_ocx_reports())
    validated.extend(list(context_manager.get_schematron_reports()))
    tables = []
    for model in validated:
        report = context_manager.get_report(model)
        if report is not None:
            tables.append(report.to_dict(exclude=['Report', 'Errors', 'Warnings', 'Assertions', 'OCX Header']))
    summary = RichTable.render('Validation results', tables)
    console.print_table(summary)
    if save:
        file_name = Path(report_folder) / f'summary_report.{report_format.value}'
        match report_format.value:
            case ReportFormat.CSV.value:
                Serializer.serialize_to_csv(tables, str(file_name.resolve()))
                console.info(f'Saved summary report to file {str(file_name.resolve())!r}')
            case ReportFormat.EXCEL.value:
                console.error(f'Option {ReportFormat.EXCEL.value!r} is not implemented')


@validate.command()
def details(
        save: Annotated[
            bool, typer.Option(help="Save a detailed report of the validated models in the report folder.")] = False,
        report_format: Annotated[ReportFormat, typer.Option(help="File format")] = ReportFormat.CSV.value,
        report_folder: Annotated[str, typer.Option(help="Path to the report folder")] = REPORT_FOLDER,

):
    """List validation detail results."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Validation Details')
    validated = list(context_manager.get_ocx_reports())
    validated.extend(list(context_manager.get_schematron_reports()))
    for model in validated:
        tables = []
        report = context_manager.get_report(model)
        if report is not None:
            tables.extend(error.to_dict() for error in report.error_details)
        detail_table = RichTable.render(f'Error Details for model: {report.source!r}', tables)
        if save:
            file_name = Path(report_folder) / f'{Path(model).stem}.{report_format.value}'
            match report_format.value:
                case ReportFormat.CSV.value:
                    Serializer.serialize_to_csv(tables, str(file_name.resolve()))
                    console.info(f'Saved detailed report to file {str(file_name.resolve())!r}')
                case ReportFormat.EXCEL.value:
                    console.error(f'Option {ReportFormat.EXCEL.value!r} is not implemented')
        console.print_table(detail_table)


@validate.command()
def readme():
    """Show the validate html page with usage examples."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.man_page(__app_name__)


@validate.command()
def headers(
        save: Annotated[bool, typer.Option(help="Save a report of the validated model in the report folder.")] = False,
        report_format: Annotated[ReportFormat, typer.Option(help="File format")] = ReportFormat.CSV.value,
        report_folder: Annotated[str, typer.Option(help="Path to the report folder")] = REPORT_FOLDER,
):
    """List the 3Docx Header information."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('3Docx Header Information')
    validated = list(context_manager.get_ocx_reports())
    tables = []
    for model in validated:
        report = context_manager.get_report(model)
        if report is not None:
            tables.append(report.ocx_header.to_dict())
    summary = RichTable.render('Headers', tables)
    console.print_table(summary)
    if save:
        file_name = Path(report_folder) / f'3docx_headers.{report_format.value}'
        match report_format.value:
            case ReportFormat.CSV.value:
                Serializer.serialize_to_csv(tables, str(file_name.resolve()))
                console.info(f'Saved summary report to file {str(file_name.resolve())!r}')
            case ReportFormat.EXCEL.value:
                console.error(f'Option {ReportFormat.EXCEL.value!r} is not implemented')


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(validate)
    return __app_name__, typer_click_object
