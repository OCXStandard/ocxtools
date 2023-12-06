#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Serializer module."""

# system imports
from dataclasses import dataclass

# 3rd party imports
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.serializers import JsonSerializer, XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

# Project imports
from ocxtools.parser.parser import MetaData


class Serializer:
    """Serializer class for 3Docx XML models."""

    def __init__(
        self,
        ocx_model: dataclass,
        pretty_print: bool = True,
        pretty_print_indent: str = "  ",
        encoding: str = "utf-8",
    ):
        """
        Args:
            ocx_model: The dataclass to serialize.
            pretty_print: True to pretty print, False otherwise.
            pretty_print_indent: Pretty print indentation.
            encoding: The encoding code.
        Params:
            _model: The dataclass to serialize.
            _config: The serializer configuration.

        """
        self._model: dataclass = ocx_model
        self._config = SerializerConfig(
            encoding=encoding,
            xml_version="1.0",
            xml_declaration=True,
            pretty_print=pretty_print,
            pretty_print_indent=pretty_print_indent,
            ignore_default_attributes=False,
            schema_location=None,
            no_namespace_schema_location=None,
            globalns=None,
        )

    def serialize_xml(self, global_ns: str = "ocx") -> str:
        """Serialize a 3Docx XML file with proper indentations.

        Returns:
              The dataclass xml serialisation.

        Raises:
            SerializeError if failing
        """
        target_ns = MetaData.namespace(self._model)
        ns_map = {global_ns: target_ns}
        serializer = XmlSerializer(context=XmlContext(), config=self._config)
        return serializer.render(self._model, ns_map=ns_map)

    def serialize_json(self) -> str:
        """Serialize a 3Docx XML model to json with proper indentations.

        Returns:
              The dataclass xml serialisation.

        Raises:
            SerializeError if failing
        """
        serializer = JsonSerializer(context=XmlContext(), config=self._config)
        return serializer.render(self._model)


class SerializerError(ValueError):
    """OCX Serializing errors."""
