#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Validator CLI."""
# System imports
import asyncio
from functools import wraps
import json
import base64
from typing import Any, Tuple
from pathlib import Path

# 3rd party imports
from loguru import logger
import typer
from typing_extensions import Annotated
import click

# Project imports
from ocxtools import VALIDATOR
from ocxtools.validator import __app_name__
from ocxtools.validator.validator_report import ValidatorReport
from ocxtools.validator.validator_client import (
    EmbeddingMethod,
    ValidationDomain, OcxValidatorClient,
    ValidatorError)
from ocxtools.renderer.renderer import RichTable
from ocxtools.utils.utilities import SourceValidator
from ocxtools.context.context_manager import get_context_manager
from ocxtools import REPORT_FOLDER

validate = typer.Typer()


def typer_async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


# @typer_async
@validate.command()
def one_model(
        model: str,
        domain: Annotated[ValidationDomain, typer.Option(help="The validator domain.")] = ValidationDomain.OCX.value,
        schema_version: Annotated[str, typer.Option(help="Input schema version.")] = "3.0.0",
        embedding: Annotated[
            EmbeddingMethod, typer.Option(help="The embedding method.")
        ] = EmbeddingMethod.BASE64.value,
        force: Annotated[bool, typer.Option(help="Validate against the input schema version.")] = False,
        save: Annotated[bool, typer.Option(help="Save the validation xml to the report folder.")] = True,
):
    """Validate one 3Docx XML file with the docker validator."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    try:
        with console.status("Waiting for the validator to finish..."):
            client = OcxValidatorClient(VALIDATOR)
            response = client.validate_one(
                ocx_model=model, domain=domain, schema_version=schema_version,
                embedding_method=embedding, force_version=force
            )
        console.section('Validate One')
        report_data = ValidatorReport.create_report(model, response)
        table = report_data.to_dict(exclude='Report')
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
        summary = RichTable.render('Validation results', [table])
        console.print_table(summary)
        if save:
            validation_report = Path(REPORT_FOLDER) / f'{Path(model).stem}_{domain.value}_validation.xml'
            with open(validation_report.resolve(), 'w') as f:
                f.write(report_data.report)
            console.info(f'Saved validation report {str(validation_report.resolve())!r}')
    except ValidatorError as e:
        console.error(f'{e}')


# @typer_async
@validate.command()
def many_models(
        directory: str,
        filter: Annotated[str, typer.Option(help="Filter models to validate.")] = "*.3docx",
        domain: Annotated[ValidationDomain, typer.Option(help="The validator domain.")] = ValidationDomain.OCX.value,
        schema_version: Annotated[str, typer.Option(help="Input schema version.")] = "3.0.0",
        embedding: Annotated[
            EmbeddingMethod, typer.Option(help="The embedding method.")
        ] = "BASE64",
        force: Annotated[bool, typer.Option(help="Validate against the input schema version.")] = False,
        interactive: Annotated[bool, typer.Option(help="Interactive mode")] = True,
):
    """Validate many 3Docx XML files with the docker validator."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    files = [model.resolve() for model in SourceValidator.filter_files(directory, filter)]
    selected_files = []
    if interactive:
        selection = typer.prompt(f'Select models (give a list of indexes, separated by spaces): '
                                 f'{[(files.index(file), file.name) for file in files]}?')
        selected_files = [str(files[int(indx)]) for indx in selection.split()]
        confirm = typer.confirm(f'Selected files: {selected_files}')
        if not confirm:
            return
    console.section('Validate Many')
    tables = []
    console.info(f'Selected files: {selected_files}')
    try:
        with console.status("Waiting for the validator to finish..."):
            client = OcxValidatorClient(VALIDATOR)
            responses = client.validate_many(
                ocx_models=selected_files,
                domain=domain, schema_version=schema_version,
                embedding_method=embedding, force_version=force
            )
        for indx, response in enumerate(json.loads(responses)):
            encoded_report = response.get('report')
            decoded_bytes = base64.b64decode(encoded_report)
            report = decoded_bytes.decode('utf-8')
            report_data = ValidatorReport.create_report(selected_files[indx], report)
            logger.info(f'Validated model {files[indx]} with result: {report_data.result}. '
                        f'Errors: {report_data.errors} '
                        f'Warnings: {report_data.warnings} '
                        f'Assertions: {report_data.assertions}')
            tables.append(report_data.to_dict(exclude='Report'))
            ctx = click.get_current_context()
            context_manager = ctx.obj
            context_manager.add_report(domain=domain, report=report_data)
            console.info(f'Created validation report for model {str(files[indx].resolve())!r}')
    except ValidatorError as e:
        console.error(f'{e}')
    summary = RichTable.render('Validation results', tables)
    console.print_table(summary)


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
        reporter = ValidatorReport()
        information = reporter.create_info_report(response)
        data = [item.to_dict() for item in information]
        table = RichTable.render(title=f'Validator server: {VALIDATOR}',
                                 data=data, caption='The validation domains and supported schema versions'
                                 )
        console.print_table(table)
    except ValidatorError as e:
        console.error(f'{e}')


@validate.command()
def list_reports():
    """List validated models with summary results.."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Validation Summaries')
    validated = list(context_manager.get_ocx_reports())
    validated.extend(list(context_manager.get_schematron_reports()))
    tables = []
    for model in validated:
        report = context_manager.get_report(model)
        if report is not None:
            tables.append(report.to_dict(exclude='Report'))
    summary = RichTable.render('Validation results', tables)
    console.print_table(summary)


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(validate)
    return __app_name__, typer_click_object
