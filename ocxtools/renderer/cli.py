#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
#
"""Renderer CLI commands."""

from pathlib import Path
from typing import Any, Tuple

# 3rd party imports
import typer

from ocxtools import config
from ocxtools.context.context_manager import get_context_manager
from ocxtools.parser.parser import OcxParser
# Project imports
from ocxtools.renderer import __app_name__
from ocxtools.renderer.renderer import XsltTransformer
from ocxtools.utils.utilities import SourceValidator

# # Renderer
RESOURCES = config.get("RendererSettings", "resource_folder")
OCX_XSLT = config.get("RendererSettings", "ocx_xslt")
SCHEMATRON_XSLT = config.get("RendererSettings", "schematron_xslt")

render = typer.Typer(help="Rendering of 3Docx models.")
ocx_parser = OcxParser()


@render.command()
def schematron():
    """List available Schematron reports."""
    # Available Schematron reports
    context_manager = get_context_manager()
    console = context_manager.get_console()
    reports = context_manager.get_schematron_reports()
    config = context_manager.get_config()
    REPORT_FOLDER = SourceValidator.mkdir(config.get("ValidatorSettings", "report_folder"))

    if models := list(reports):
        indx = typer.prompt(f'Select a model report number: {list(enumerate(models))}')
        model = models[int(indx)]
        typer.confirm(f'Render the html report for model {model}?')
        report_data = context_manager.get_report(model)
        xslt_file = Path(RESOURCES) / SCHEMATRON_XSLT
        transformer = XsltTransformer(str(xslt_file.resolve()))
        output_file = Path(transformer.render(data=report_data.report, source_file=model,
                                              output_folder=REPORT_FOLDER))
        console.info(f'Created html report {output_file!r}')
    else:
        console.warning('You have not validated any models with the schematron validator.'
                        ' Execute "validate one-model <model> --domain=schematron"')


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(render)
    return __app_name__, typer_click_object
