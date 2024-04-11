#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module for parsing a 3Docx model."""

import dataclasses
# system imports
from abc import ABC
from dataclasses import dataclass
from typing import Dict, Iterator

# 3rd party imports
import lxml.etree
from loguru import logger
from lxml.etree import Element
from xsdata.exceptions import ParserError
from xsdata.formats.dataclass.context import XmlContext, XmlContextError
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.parsers.handlers import LxmlEventHandler

from ocxtools.exceptions import XmlParserError
# Project imports
from ocxtools.interfaces.interfaces import (IObservable, IParser,
                                            ObservableEvent)
from ocxtools.loader.loader import DeclarationOfOcxImport, DynamicLoader
from ocxtools.utils.utilities import OcxVersion, SourceValidator


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
        return declaration[declaration.rfind(".") + 1: -2]

    @staticmethod
    def namespace(data_class: dataclass) -> str:
        """Get the OCX namespace

        Args:
            data_class: The dataclass instance

        Returns:
            The namespace of the dataclass
        """
        return MetaData.meta_class_fields(data_class).get("namespace")

    @staticmethod
    def name(data_class: dataclass) -> str:
        """Get the OCX name

        Args:
            data_class: The dataclass instance

        Returns:
            The name of the OCX type
        """
        return MetaData.meta_class_fields(data_class).get("name")


class OcxNotifyParser(IObservable, ABC):
    """Ocx notification parser class for 3Docx XML files.

     Args:
         fail_on_unknown_properties: Don't bail out on unknown properties.
         fail_on_unknown_attributes: Don't bail out on unknown attributes
         fail_on_converter_warnings: bool = Convert warnings to exceptions

     """

    def __init__(
            self,
            fail_on_unknown_properties: bool = False,
            fail_on_unknown_attributes: bool = False,
            fail_on_converter_warnings: bool = True,
    ):
        context = XmlContext()
        parser_config = ParserConfig(
            fail_on_unknown_properties=fail_on_unknown_properties,
            fail_on_unknown_attributes=fail_on_unknown_attributes,
            fail_on_converter_warnings=fail_on_converter_warnings,
            class_factory=self.class_factory)
        self._parser = XmlParser(config=parser_config, context=context)
        self._subscribers = set()

    def subscribe(self, observer):
        self._subscribers.add(observer)
        return

    def unsubscribe(self, observer):
        self._subscribers.remove(observer)
        return

    def update(self, event: ObservableEvent, payload: Dict):
        for observer in self._subscribers:
            observer.update(event, payload)

    def class_factory(self, clazz, params):
        """Custom class factory method"""
        name = clazz.__name__
        new_data_class = clazz(**params)
        # Broadcast an update
        namespace = MetaData.namespace(clazz)
        # name = MetaData.name(clazz)
        fields = MetaData.meta_class_fields(clazz)
        logger.debug(f'Meta fields: {fields}')
        tag = '{' + namespace + '}' + name
        self.update(ObservableEvent.DATACLASS, {'name': tag, 'object': new_data_class})
        return new_data_class

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
            return self._parser.parse(root, ocx_module.OcxXml)
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


    def parse_element(self, element: Element, ocx_module) -> dataclass:
        """Parse a 3Docx XML element and return the dataclass.

        Args:
            element: The 3Docx XML Element to parse.

        Returns:
            The element dataclass instance.
        """
        try:
            return self._parser.parse(element, ocx_module)
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


class OcxParser(IParser, ABC):
    """OcxParser class for 3Docx XML files.

    Args:
        fail_on_unknown_properties: Don't bail out on unknown properties.
        fail_on_unknown_attributes: Don't bail out on unknown attributes
        fail_on_converter_warnings: bool = Convert warnings to exceptions

    """

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
            ocx_parser = XmlParser(
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
    #         ocx_parser = OcxEventParser(
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
