#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""This module provides the ocx_attribute_reader app functionality."""
# System imports
from pathlib import Path
from typing import Any, Tuple

# 3rd party imports
import typer
from typing_extensions import Annotated

from ocxtools.exceptions import XmlParserError
from ocxtools.parser.parser import OcxParser

# Project imports
from ocxtools.serializer.serializer import Serializer
from ocxtools.serializer import __app_name__
from ocxtools import SERIALIZER_SUFFIX, JSON_INDENT
from ocxtools.context.context_manager import get_context_manager

serialize = typer.Typer()
ocx_parser = OcxParser()


@serialize.command()
def xml(
    model: Path,
    post_fix: Annotated[str, typer.Option(help="The model file name post fix")] = SERIALIZER_SUFFIX,
):
    """Serialize a 3Docx model to file"""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    try:
        ocx_obj = ocx_parser.parse(str(model))
        # Serialize
        output = model.parent.joinpath(f"{model.stem}{post_fix}{model.suffix}")
        output = output.resolve()
        serializer = Serializer(ocx_obj)
        with output.open("w") as fp:
            fp.write(serializer.serialize_xml())
        console.print(f"Pretty printed file {output!r}")
        # Check for any warnings issued during serialization
        # for warning_message in warnings:
        #     print(f"Warning: {warning_message}")

    except XmlParserError as e:
        console.error(e)


@serialize.command()
def json(
    model: Path,
    indent: Annotated[int, typer.Option(help="The JSON indentation level.")] = JSON_INDENT,
):
    """Serialize an 3Docx model to json."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    try:
        ocx_obj = ocx_parser.parse(str(model))
        # Serialize
        output = model.parent.joinpath(f"{model.stem}.json")
        output = output.resolve()
        serializer = Serializer(ocx_obj)
        with output.open("w") as fp:
            fp.write(serializer.serialize_json())
        console.print(f"Serialised JSON: {output!r}")
    except XmlParserError as e:
        console.error(e)


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(serialize)
    return __app_name__, typer_click_object
