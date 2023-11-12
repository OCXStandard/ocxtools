#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""OCX Converter module."""

# system imports
import sys
from pathlib import Path
from typing import Tuple, List
import copy
from dataclasses import fields
import json


# 3rd party imports
from loguru import logger
import lxml.etree
from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.parsers.handlers import LxmlEventHandler
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.context import XmlContextError
from xsdata.exceptions import ParserError
from xsdata.formats.dataclass.parsers import JsonParser

# Project imports
from ocxtools.ocx_version_manager import VersionManager
from ocxtools.loader import DynamicLoader, DeclarationOfOcxImport



def deep_copy(data_class) -> object:
    """Recursively copy a data class"""
    field_names = VersionManager.get_dataclass_field_names(data_class)
    for name in data_class.__dataclass_fields__:
        value = getattr(data_class, name)
        print(name, value)



class Converter:
    """The OCX converter class.

    """
    def __init__(self):
        pass

    @staticmethod
    def serialize_ocx(ocx_object, namespace: str, file_name: str):
        """Serialize a dataclass object to file

        """
        config = SerializerConfig(pretty_print=True)
        serializer = XmlSerializer(config)
        with open(file_name, 'w') as f:
#            f.write(serializer.render(ocx_object, ns_map={'ocx': namespace}))
            f.write(serializer.render(ocx_object))

    @staticmethod
    def pretty_print_ocx(ocx_model: Path) -> Tuple[bool, Path]:
        """Pretty print a xml file with proper indentations.
        
        Args:
            ocx_model: The 3Docx model to be pretty printed
        
        Returns:
              a tuple (bool, Path). If tuple[0] is True, the tuple will also contain the Path object to the pretty printed output
        """
        result = False
        stem = Path(ocx_model).stem
        file = stem
        parser_config = ParserConfig(fail_on_unknown_properties=False, fail_on_unknown_attributes=False)
        parser = XmlParser(handler=LxmlEventHandler, config=parser_config)
        tree = lxml.etree.parse(str(ocx_model))
        root = tree.getroot()
        version = Converter.ocx_version(ocx_model)
        namespace = Converter.ocx_namespace(ocx_model)
        declaration = DeclarationOfOcxImport('ocx', version)
        ocx_module = DynamicLoader.load_module(declaration)
        if root is not None and ocx_module is not None:
            # Load target schema version module
            try:
                data = parser.parse(root, ocx_module.OcxXml)
                file = f'{stem}_pp.3Docx'
                namespace = ''
                Converter.serialize_ocx(data, namespace, file)
                result = True
            except ImportError as e:
                logger.error(e)
            except XmlContextError as e:
                logger.error(e)
            except ParserError as e:
                logger.error(e)
        else:
            logger.error(f'Can not find root element ocxXML in the document {ocx_model.resolve()}')
        return result, Path(file)

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
    def convert( ocx_model: Path, to_version: str) -> bool:
        """"Convert an OCX model from a version ``X`` to Version ``Y``."""
        # Model version
        module = 'ocx'
        old_ocx = Converter.parse_model(ocx_model)
        # config = ParserConfig(class_factory=VersionManager.ocx_class_factory)
        # parser = JsonParser(config=config)
        json_string = json.dumps({'vessel': [], 'class_catalogue': [], 'units_ml': []})
        new_ocx = VersionManager.dynamic_import_class(module, to_version,'OcxXml')()
        if old_ocx and new_ocx:
            if old_ocx.header:
                new_header = VersionManager.dynamic_import_class(module, to_version,'Header')(time_stamp = old_ocx.header.time_stamp)
                new_ocx.header = new_header
            namespace = ''
            converted_file = f'({ocx_model.stem}_converted'
            Converter.serialize_ocx(new_ocx, namespace, converted_file)
            return True
        return False

    @staticmethod
    def parse_model(ocx_model) -> object:
        """Parse an OCX model and return the root object.

        Args:
            ocx_model: The 3Docx xml file to parse.

        Returns:
            The root object of the parsed model.

        """
        data = None
        parser_config = ParserConfig(fail_on_unknown_properties=False, fail_on_unknown_attributes=False)
        parser = XmlParser(handler=LxmlEventHandler, config=parser_config)
        tree = lxml.etree.parse(str(ocx_model))
        root = tree.getroot()
        version = Converter.ocx_version(ocx_model)
        ocx_module = VersionManager.dynamic_import('ocx', version)
        if root is not None and ocx_module is not None:
            # Load target schema version module
            try:
                data = parser.parse(root, ocx_module.OcxXml)
            except ImportError as e:
                logger.error(e)
            except XmlContextError as e:
                logger.error(e)
            except ParserError as e:
                logger.error(e)
        return data

