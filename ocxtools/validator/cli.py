#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Validator CLI."""
# System imports
from pathlib import Path
from typing import Any, Tuple

import click
# 3rd party imports
from loguru import logger
import typer
from typing_extensions import Annotated
import click
from rich.progress import track
# Project imports
from ocxtools import VALIDATOR, REPORT_FOLDER, RESOURCES, XSLT_EN
from ocxtools.validator.validator_report import ValidatorReport
from ocxtools.validator.validator_client import EmbeddingMethod, OcxValidatorCurlClient, ValidatorError
from ocxtools.renderer.renderer import RichTable
from ocxtools.console.console import CliConsole
from ocxtools.utils.utilities import SourceValidator

validate = typer.Typer()

console = CliConsole()


@validate.command()
def one_model(
        model: str,
        domain: Annotated[str, typer.Option(help="The validator domain.")] = "ocx",
        schema_version: Annotated[str, typer.Option(help="Input schema version.")] = "3.0.0",
        embedding: Annotated[
            EmbeddingMethod, typer.Option(help="The embedding method.")
        ] = "BASE64",
        force: Annotated[bool, typer.Option(help="Validate against the input schema version.")] = False,
):
    """Validate one 3Docx XML file with the docker validator."""
    client = OcxValidatorCurlClient(VALIDATOR)
    model = str(model)
    try:
        response = client.validate_one(
            ocx_model=model, domain=domain, schema_version=schema_version,
            embedding_method=embedding, force_version=force
        )
        console.print_section('Validation Results')
        report_data = ValidatorReport.create_report(model, response)
        table = report_data.to_dict(exclude='Report')
        logger.info(f'Validated model {model} with result: {report_data.result}. '
                    f'Errors: {report_data.errors} '
                    f'Warnings: {report_data.warnings} '
                    f'Assertions: {report_data.assertions}')
        ctx = click.get_current_context()
        context_manager = ctx.obj
        context_manager.add_ocx_report(model, report_data.report)
        match report_data.result:
            case 'SUCCESS':
                console.print(report_data.result)
            case _:
                console.print_error(report_data.result)
                # xslt = Path(RESOURCES) / XSLT_EN
                # transformer = XsltTransformer(str(xslt))
                # context = click.get_current_context().obj
                # report = report_data.report  # .encode(encoding='utf-8')
                # report_name = transformer.render(data=report,
                #                                 source_file=model,
                #                                 output_folder=REPORT_FOLDER)
                # if context is not None:
                # context.add_ocx_report(model, report_name)
                # console.print(f'Created report {report_name}')
        summary = RichTable.render('Validation results', [table])
        console.print_table(summary)
    except ValidatorError as e:
        console.print_error(f'{e}')


@validate.command()
def many_models(
        directory: str,
        filter: Annotated[str, typer.Option(help="Filter models to validate.")] = "*.3docx",
        domain: Annotated[str, typer.Option(help="The validator domain.")] = "ocx",
        schema_version: Annotated[str, typer.Option(help="Input schema version.")] = "3.0.0",
        embedding: Annotated[
            EmbeddingMethod, typer.Option(help="The embedding method.")
        ] = "BASE64",
        force: Annotated[bool, typer.Option(help="Validate against the input schema version.")] = False,
        interactive: Annotated[bool, typer.Option(help="Interactive mode")] = True,
):
    """Validate many 3Docx XML files with the docker validator."""
    client = OcxValidatorCurlClient(VALIDATOR)
    files = [model.name for model in SourceValidator.filter_files(directory, filter)]
    if interactive:
        confirm = typer.confirm(f'Validate all models {files}?')
        if not confirm:
            return
    console.print_section('Validation Results')
    tables = []
    for file in SourceValidator.filter_files(directory, filter):
        model = str(file.resolve())
        model_name = file.name
        console.print(f'Validating {model_name}')
        try:
            response = client.validate_one(
                ocx_model=model, domain=domain, schema_version=schema_version,
                embedding_method=embedding, force_version=force
            )
            report_data = ValidatorReport.create_report(model_name, response)
            logger.info(f'Validated model {model} with result: {report_data.result}. '
                        f'Errors: {report_data.errors} '
                        f'Warnings: {report_data.warnings} '
                        f'Assertions: {report_data.assertions}')
            tables.append(report_data.to_dict(exclude = 'Report'))
            ctx = click.get_current_context()
            context_manager = ctx.obj
            context_manager.add_ocx_report(model, report_data.report)
        except ValidatorError as e:
            console.print_error(f'{e}')
    summary = RichTable.render('Validation results', tables)
    console.print_table(summary)


@validate.command()
def info():
    """Verify that the Docker validator is alive and obtain the available validation options."""
    ocx_validator = OcxValidatorCurlClient(VALIDATOR)
    try:
        response = ocx_validator.get_validator_info()
        reporter = ValidatorReport()
        information = reporter.create_info_data(response)
        data = [item.to_dict() for item in information]
        table = RichTable.render(title=f'Validator server: {ocx_validator.validator_service()}',
                                 data=data, caption='The validation domains and supported schema versions'
                                 )
        console.print_section('Validator Info')
        console.print_table(table)
    except ValidatorError as e:
        console.print_error(f'{e}')


@validate.command()
def gui(
        domain: Annotated[str, typer.Option(help="The validator domain.")] = "ocx",
):
    """Use the validator GUI to validate a model for a given validation domain."""
    try:
        command = f'cmd /c start http://localhost:8080/{domain}/upload'
        console.run_sub_process(command)
    except ValidatorError as e:
        console.print_error(f'{e}')


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(validate)
    return "validate", typer_click_object
