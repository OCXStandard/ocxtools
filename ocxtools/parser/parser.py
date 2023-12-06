#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module for parsing a 3Docx model."""

import dataclasses

# system imports
from abc import ABC
from dataclasses import dataclass
from typing import Dict, Iterator

import lxml.etree

# 3rd party imports
from loguru import logger
from xsdata.exceptions import ParserError
from xsdata.formats.dataclass.context import XmlContext, XmlContextError
from xsdata.formats.dataclass.parsers import UserXmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.parsers.handlers import LxmlEventHandler
from xsdata.formats.dataclass.parsers.mixins import XmlHandler

from ocxtools.exceptions import XmlParserError

# Project imports
from ocxtools.interfaces.interfaces import IParser
from ocxtools.loader.loader import DeclarationOfOcxImport, DynamicLoader
from ocxtools.utils.utilities import OcxVersion, SourceValidator


class OcxXmlParser(UserXmlParser):
    def __init__(self, config: ParserConfig, context: XmlContext, handler=XmlHandler):
        super().__init__(config, context, handler)
        self._object_map = {}

    def end(self, queue: list, objects: list, qname: str, text: str, tail: str) -> bool:
        """Override method and build the mapping table between XML elements and dataclass names."""
        if result := super().end(queue, objects, qname, text, tail):
            # logger.debug(f'QName: {qname}, object_name: {class_name}')
            self._object_map[qname] = MetaData.class_name(objects[-1][1])

    def get_mapping(self) -> Dict:
        """Obtain the mapping table."""
        return self._object_map


not_supported = ["FrameTables", "VesselGrid", "CoordinateSystem"]


class OcxParser(IParser, ABC):
    """IParser class for 3Docx XML files."""

    def __init__(
        self,
        fail_on_unknown_properties: bool = False,
        fail_on_unknown_attributes: bool = False,
        fail_on_converter_warnings: bool = True,
    ):
        self._context = XmlContext()
        self._parser_config = ParserConfig(
            fail_on_unknown_properties=fail_on_unknown_properties,
            fail_on_unknown_attributes=fail_on_unknown_attributes,
            fail_on_converter_warnings=fail_on_converter_warnings,
        )

    def parse(self, xml_file: str) -> dataclass:
        """Parse a 3Docx XML model and return the root dataclass.

        Args:
            xml_file: The 3Docx xml file or url to parse.

        Returns:
            The root dataclass instance of the parsed 3Docx XML.
        """
        try:
            file_path = SourceValidator.validate(xml_file)
            tree = lxml.etree.parse(xml_file)
            root = tree.getroot()
            version = OcxVersion.get_version(file_path)
            declaration = DeclarationOfOcxImport("ocx", version)
            # Load target schema version module
            ocx_module = DynamicLoader.import_module(declaration)
            ocx_parser = OcxXmlParser(
                handler=LxmlEventHandler,
                config=self._parser_config,
                context=self._context,
            )
            return ocx_parser.parse(root, ocx_module.OcxXml)
        except lxml.etree.XMLSyntaxError as e:
            logger.error(e)
            raise XmlParserError(e) from e
        except ImportError as e:
            logger.error(e)
            raise XmlParserError from e
        except XmlContextError as e:
            logger.error(e)
            raise XmlParserError from e
        except ParserError as e:
            logger.error(e)
            raise XmlParserError from e

    # def convert(self, ocx_model: str, version: str) -> dataclass:
    #     """Convert a 3Docx XML model to another schema version and return the root dataclass instance.
    #
    #     Args:
    #         version: Convert the model to this version
    #         ocx_model: The 3Docx XML file or url to parse.
    #
    #     Returns:
    #         The root object of the converted model.
    #     """
    #     data = None
    #     exists, file_path = SourceValidator.exist(ocx_model)
    #     if exists:
    #         tree = lxml.etree.parse(ocx_model)
    #         root = tree.getroot()
    #         # The target model version schema
    #         target_module = DeclarationOfOcxImport("ocx", version)
    #         converter = OcxConverter(target_module)
    #         # The schema for the source model version
    #         source_version = OcxVersion.get_version(ocx_model)
    #         source_module = DeclarationOfOcxImport("ocx", source_version)
    #         ocx_module = DynamicLoader.import_module(source_module)
    #         parser_config = ParserConfig(
    #             fail_on_unknown_properties=False,
    #             fail_on_unknown_attributes=False,
    #             class_factory=converter.class_factory,
    #         )
    #         ocx_parser = OcxXmlParser(
    #             handler=LxmlEventHandler, config=parser_config, context=XmlContext()
    #         )
    #         if root is not None and ocx_module is not None:
    #             try:
    #                 data = ocx_parser.parse(root, ocx_module.OcxXml)
    #             except ImportError as e:
    #                 logger.error(e)
    #             except XmlContextError as e:
    #                 logger.error(e)
    #             except ParserError as e:
    #                 logger.error(e)
    #     else:
    #         logger.error(f"The file {ocx_model} does not exist.")
    #     return data

    def iterator(self, ocx_model: str) -> Iterator:
        data_class = self.parse(ocx_model)
        # print(MetaData.meta_class_fields(data_class))
        return iter(dataclasses.asdict(data_class))


class MetaData:
    """Dataclass metadata."""

    @staticmethod
    def meta_class_fields(data_class: dataclass) -> Dict:
        """
        Return the dataclass metadata.

        Args:
            data_class: The dataclass instance

        Returns:
            The metadata of the class
        """
        return dict(data_class.Meta.__dict__.items())

    @staticmethod
    def class_name(data_class: dataclass) -> str:
        """Return the name of the class"""
        declaration = str(data_class.__class__)
        return declaration[declaration.rfind(".") + 1 : -2]

    @staticmethod
    def namespace(data_class: dataclass) -> str:
        """Get the OCX namespace

        Args:
            data_class: The dataclass instance

        Returns:
            The namespace of the dataclass
        """
        return MetaData.meta_class_fields(data_class).get("namespace")
