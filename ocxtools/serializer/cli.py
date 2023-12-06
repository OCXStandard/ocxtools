#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""This module provides the ocx_attribute_reader app functionality."""
# System imports
from pathlib import Path
from typing import Any, Tuple
import warnings

# 3rd party imports
import typer
from typing_extensions import Annotated

from ocxtools.exceptions import XmlParserError
from ocxtools.parser.parser import OcxParser

# Project imports
from ocxtools.serializer.serializer import Serializer

serialize = typer.Typer()
ocx_parser = OcxParser()


@serialize.command()
def xml(
    model: Path,
    post_fix: Annotated[str, typer.Option(help="The model file name post fix")] = "_pp",
):
    """Serialize a 3Docx model to file"""
    try:
        ocx_obj = ocx_parser.parse(str(model))
        # Serialize
        output = model.parent.joinpath(f"{model.stem}{post_fix}{model.suffix}")
        output = output.resolve()
        serializer = Serializer(ocx_obj)
        with output.open("w") as fp:
            fp.write(serializer.serialize_xml())
        print(f"Pretty printed file {output!r}")
        # Check for any warnings issued during serialization
        # for warning_message in warnings:
        #     print(f"Warning: {warning_message}")

    except XmlParserError as e:
        print(e)


@serialize.command()
def json(
    model: Path,
    indent: Annotated[int, typer.Option(help="The JSON indentation level.")] = 4,
):
    """Serialize an 3Docx model to json."""
    try:
        ocx_obj = ocx_parser.parse(str(model))
        # Serialize
        output = model.parent.joinpath(f"{model.stem}.json")
        output = output.resolve()
        serializer = Serializer(ocx_obj)
        with output.open("w") as fp:
            fp.write(serializer.serialize_json())
        print(f"Serialised JSON: {output!r}")
    except XmlParserError as e:
        print(e)


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(serialize)
    return "serialize", typer_click_object
