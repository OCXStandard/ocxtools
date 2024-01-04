#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""This module provides the ocx_attribute_reader app functionality."""
# System imports
from pathlib import Path
from typing import Tuple, Any
# 3rd party imports
import typer
# Project imports
from ocxtools.renderer.renderer import RichTable
from ocxtools.exceptions import XmlParserError
from ocxtools.parser.parser import OcxNotifyParser
from ocxtools.reporter.reporter import OcxReporter
from ocxtools.context.context_manager import get_context_manager
from ocxtools.reporter import __app_name__

report = typer.Typer(help="Reporting of 3Docx attributes")


@report.command()
def count_elements(
        model: Path,
):
    """Report the count of OCX types in a model."""
    selection = typer.prompt("Select the OCX entities as a list of names (blank space as separator). "
                             "Enter 'All' to count all the objects in the model", type=str)
    if selection.lower() == "all":
        selection = ["All"]
    else:
        selection = selection.split()
        if not typer.confirm(f'You entered: {selection}'):
            return
    try:
        context_manager = get_context_manager()
        console = context_manager.get_console()
        console.section('Report Element Count')
        ocx_parser = OcxNotifyParser()
        reporter = OcxReporter(ocx_parser)
        ocx_parser.parse(str(model))
        # report
        element_count = reporter.element_count(selection=selection)
        table = RichTable.render('Element Count', element_count)
        console.print_table(table)
    except XmlParserError as e:
        print(e)


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(report)
    return __app_name__, typer_click_object
