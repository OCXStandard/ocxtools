#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""This module provides the ocx_attribute_reader app functionality."""
# System imports
from pathlib import Path
from typing import Any, Tuple

# 3rd party imports
import typer
from typing_extensions import Annotated

# Project imports
from ocxtools.exceptions import ValidatorError
from ocxtools.renderer.renderer import TableRender
from ocxtools.validator.factory import ValidatorFactory
from ocxtools.validator.validator_client import EmbeddingMethod, OcxValidatorClient

docker_validator = "http://localhost:8080"

validate = typer.Typer()


@validate.command()
def one(
    model: Path,
    domain: Annotated[str, typer.Option(help="The validator domain.")] = "ocx",
    embedding: Annotated[
        EmbeddingMethod, typer.Option(help="The embedding method.")
    ] = "BASE64",
):
    """Validate one 3Docx XML file with the docker validator."""
    ocx_validator = OcxValidatorClient(docker_validator)
    try:
        response = ocx_validator.validate_one(str(model), domain, embedding)
        report = ValidatorFactory.create_report_data(response)
        print(TableRender.render(report.counters.to_dict()))
        print(TableRender.render(report.overview.to_dict()))
        # print(tabulate(report.counters.to_dict(), headers='keys'))
        # print(tabulate(report.overview.to_dict(), headers= 'keys'))
        for error in report.reports:
            print(TableRender.render(error.to_dict()))
    except ValidatorError as e:
        print(e)


@validate.command()
def info():
    """Verify that the Docker validator is alive and obtain the available validation options."""
    ocx_validator = OcxValidatorClient(docker_validator)
    try:
        response = ocx_validator.get_validator_info()
        information = ValidatorFactory.create_info_data(response)

        print(f"Validator service:  {ocx_validator.validator_service()!r}")
        for item in information:
            print(item.domain, item.validation_type, item.description)
    except ValidatorError as e:
        print(f"The Docker validator returned an error: {e}")


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(validate)
    return "validate", typer_click_object
