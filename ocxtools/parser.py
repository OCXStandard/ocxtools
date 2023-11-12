#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module for parsing a 3Docx model."""

# system imports
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Iterator
import dataclasses
from dataclasses import dataclass
from collections import defaultdict

# 3rd party imports
from loguru import logger
import lxml.etree
from lxml.etree import QName
from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.parsers.handlers import LxmlEventHandler
from xsdata.formats.dataclass.parsers import XmlParser, UserXmlParser
from xsdata.formats.dataclass.parsers.mixins import XmlHandler
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.context import XmlContextError, XmlContext
from xsdata.exceptions import ParserError
from pathlib import Path
# Project imports
from ocxtools.loader import DynamicLoader, DeclarationOfOcxImport
from ocxtools.converter import OcxConverter


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


class SourceValidator(ABC):
    """Abstract Methods for validating the existence of a data source."""

    @abstractmethod
    def exist(self, source: str) -> bool:
        """
        Validate the existence of a data source.

        Args:
            source: The string pointing to a source.

        Returns:
              True if the source exists, False otherwise.
        """
        pass


class FileValidator(SourceValidator):
    """
    Concrete method for validating the existence of a file.

    """

    @classmethod
    def exist(cls, file: str) -> Tuple[bool, Path]:
        """
        Validate the existence of a file.

        Args:
            file: The path pointing to a file.

        Returns:
              True if the file exists, False otherwise.
        """
        file_path = Path(file)
        return file_path.exists(), file_path


class Parser(ABC):
    """Abstract Parser interface."""

    @abstractmethod
    def parse(self, model) -> dataclass:
        """
        Abstract method for parsing a data model,

        Args:
            model: the dta model source

        Returns:
            the root of the parsed data model.
        """
        pass

    @abstractmethod
    def iterator(self, model) -> Iterator:
        """
        Abstract method for iterating a data model.

        Args:
            model: the data model to iterate on.
        Returns:
             An iterator
        """
        pass

not_supported = ['FrameTables', 'VesselGrid', 'CoordinateSystem']



class OcxParser(Parser, ABC):
    """Parser class for 3Docx XML files."""

    def parse(self, ocx_model: str) -> dataclass:
        """Parse a 3Docx model and return the root object.

        Args:
            ocx_model: The 3Docx xml file to parse.

        Returns:
            The root object of the parsed model.
        """
        data = None
        exists, file_path = FileValidator.exist(ocx_model)
        if exists:
            tree = lxml.etree.parse(ocx_model)
            root = tree.getroot()
            version = self.ocx_version(file_path)
            declaration = DeclarationOfOcxImport('ocx', version)
            # Load target schema version module
            ocx_module = DynamicLoader.load_module(declaration)
            parser_config = ParserConfig(fail_on_unknown_properties=False, fail_on_unknown_attributes=False)
            ocx_parser = OcxXmlParser(handler=LxmlEventHandler, config=parser_config, context=XmlContext())
            if root is not None and ocx_module is not None:
                try:
                    data = ocx_parser.parse(root, ocx_module.OcxXml)
                except ImportError as e:
                    logger.error(e)
                except XmlContextError as e:
                    logger.error(e)
                except ParserError as e:
                    logger.error(e)
        else:
            logger.error(f'The file {ocx_model} does not exist.')
        return data

    def convert(self, ocx_model: str, version: str) -> dataclass:
        """Convert a 3Docx model to another schema version and return the root object.

        Args:
            version: Convert the model to this version
            ocx_model: The 3Docx xml file to parse.

        Returns:
            The root object of the converted model.
        """
        data = None
        exists, file_path = FileValidator.exist(ocx_model)
        if exists:
            tree = lxml.etree.parse(ocx_model)
            root = tree.getroot()
            target_module = DeclarationOfOcxImport('ocx', version)
            converter = OcxConverter(target_module)
            # Load soyrce schema version module
            source_version = self.ocx_version(file_path)
            source_module = DeclarationOfOcxImport('ocx', source_version)
            ocx_module = DynamicLoader.load_module(source_module)
            parser_config = ParserConfig(fail_on_unknown_properties=False, fail_on_unknown_attributes=False,
                                         class_factory=converter.class_factory)
            ocx_parser = OcxXmlParser(handler=LxmlEventHandler, config=parser_config, context=XmlContext())
            if root is not None and ocx_module is not None:
                try:
                    data = ocx_parser.parse(root, ocx_module.OcxXml)
                except ImportError as e:
                    logger.error(e)
                except XmlContextError as e:
                    logger.error(e)
                except ParserError as e:
                    logger.error(e)
        else:
            logger.error(f'The file {ocx_model} does not exist.')
        return data

    def iterator(self, ocx_model: str) -> Iterator:
        data_class = self.parse(ocx_model)
        # print(MetaData.meta_class_fields(data_class))
        return iter(dataclasses.asdict(data_class))

    @staticmethod
    def ocx_namespace(ocx_model: Path) -> str:
        """Return the OCX schema namespace of the model.

        Args:
            ocx_model: The 3Docx model

        Returns:
              The OCX schema version of the model.
        """
        namespace = 'NA'
        content = ocx_model.read_text().split()
        for item in content:
            if 'xmlns:ocx' in item:
                namespace = item[item.find('=') + 2:-1]
        return namespace

    @staticmethod
    def ocx_version(ocx_model: Path) -> str:
        """Return the OCX schema version of the model.

        Args:
            ocx_model: The 3Docx model

        Returns:
              The OCX schema version of the model.
        """
        version = 'NA'
        content = ocx_model.read_text().split()
        for item in content:
            if 'schemaVersion' in item:
                version = item[item.find('=') + 2:-1]
        return version


class MetaData:
    """Dataclass metadata."""

    @staticmethod
    def meta_class_fields(data_class) -> Dict:
        """
        Return the dataclass metadata.

        Args:
            data_class: The dataclass instance

        Returns:
            The metadata of the class
        """
        return dict(data_class.Meta.__dict__.items())

    @staticmethod
    def class_name(data_class) -> str:
        """Return the name of the class"""
        declaration = str(data_class.__class__)
        return declaration[declaration.rfind('.') + 1: -2]
