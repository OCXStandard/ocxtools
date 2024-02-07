#  Copyright (c) 2023-2024. OCX Consortium https://3docx.org. See the LICENSE
"""OCX reporter module"""

# System imports
from collections import defaultdict
from typing import Any, Dict, List, Union
from pathlib import Path
from itertools import groupby
from dataclasses import dataclass, is_dataclass
import pandas as pd


# Third party
import lxml
from lxml.etree import Element, QName
from loguru import logger
import arrow
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.handlers import LxmlEventHandler
from xsdata.exceptions import ParserError
# project imports
from ocxtools.parser.parser import OcxNotifyParser
from ocxtools.dataclass.dataclasses import (OcxHeader, ReportElementCount, ElementCount, ReportDataFrame,
                                            ReportType)
from ocxtools.interfaces.interfaces import ABC, IObserver, ObservableEvent
from ocxtools.utils.utilities import SourceValidator, OcxVersion
from ocxtools.exceptions import ReporterError, SourceError
from ocx_schema_parser.xelement import LxmlElement
from ocxtools.loader.loader import DeclarationOfOcxImport, DynamicLoader, DynamicLoaderError


def is_substring_in_list(substring, string_list):
    """

    Args:
        substring: The search string
        string_list: List of strings

    Returns:
        True if the substring is found, False otherwise.
    """
    return any(substring in string for string in string_list)


def flatten_data(
        data: Any, parent_key: str = '',
        max_depth: int = float('inf'),
        depth: int = 0, sep: str = '.') -> Dict[str, Any]:
    """
    Flattens nested data structures into a dictionary.

    Args:
        data (Any): The data to be flattened.
        parent_key (str): The parent key to be prepended to the flattened keys. Defaults to an empty string.
        max_depth (int): The maximum depth to flatten the data. Defaults to infinity.
        depth (int): The current depth of recursion. Defaults to 0.
        sep (str): The separator to use between keys. Defaults to '.'.

    Returns:
        Dict[str, Any]: The flattened data as a dictionary.

    Examples:
        >>> data = {'a': {'b': {'c': 1}}, 'd': [2, 3]}
        >>> flatten_data(data)
        {'a.b.c': 1, 'd': [2, 3]}
    """
    flat_data = {}
    if is_dataclass(data):
        data = data.__dict__
    for key, value in data.items():
        if is_dataclass(value):
            value = value.__dict__
        if isinstance(value, dict):
            if depth < max_depth:
                flat_data.update(flatten_data(value, parent_key + key + sep, max_depth, depth + 1))
            else:
                flat_data[parent_key + key] = value
        elif isinstance(value, list):
            if all(isinstance(item, (int, float, str)) for item in value) or depth == max_depth:
                flat_data[parent_key + key] = value
            else:
                for i, item in enumerate(value):
                    flat_data.update(flatten_data(item, f"{parent_key}{key}{i}{sep}", max_depth, depth + 1))
        else:
            flat_data[parent_key + key] = value
    return flat_data


class OcxReportFactory:
    """Reporter factory class"""

    @staticmethod
    def create_header(root: Element, ocx_model: str) -> OcxHeader:
        """
        Create the OcxHeader dataclass from the XML content.
        Args:
            root: The XML root
            ocx_model: The 3Docx file path.

        Returns:
            The 3Docx header dataclass
        """
        xml_header = LxmlElement.find_child_with_name(root, 'Header')
        namespace = LxmlElement.get_namespace(root)
        version = root.get('schemaVersion')
        return OcxHeader(
            source=ocx_model,
            schema_version=version,
            namespace=namespace,
            time_stamp=arrow.get(xml_header.get('time_stamp')).format(),
            author=xml_header.get('author'),
            name=xml_header.get('name'),
            originating_system=xml_header.get('originating_system'),
            organization=xml_header.get('organization'),
            application_version=xml_header.get('application_version'),
        )

    @staticmethod
    def element_count(model: str, objects: Dict) -> ReportElementCount:
        """
        Element count report
        Args:
            model: The source XML file
            objects: List of 3Docx objects

        Returns:
            The element count report.
        """
        try:
            elements = [ElementCount(namespace=QName(key).namespace, name=LxmlElement.strip_namespace_tag(key),
                                     count=len(objects[key])) for key in sorted(objects)]
            return ReportElementCount(
                source=model,
                elements=elements,
                count=sum(element.count for element in elements),
                unique=len(elements)
            )
        except TypeError as e:
            logger.error(f'{e}')
            raise ReporterError(e) from e

    @staticmethod
    def element_primitives(ocx_element: dataclass) -> dict[Any, Any]:
        """
        Returns a dictionary containing the attributes of the given OCX element.

        Args:
            ocx_element: The OCX element to generate the report for.

        Returns:
            dict[Any, Any]: A dictionary containing the attributes of the OCX element, excluding non-primitive types.
        """
        return {
            key: item
            for key, item in ocx_element.__dict__.items()
            if type(item) in [int, float, str]
        }

    @staticmethod
    def element_to_dataframe(model: str, report_type: ReportType, data: List[dataclass], depth: int) -> ReportDataFrame:
        """
        Converts a list of dataclass objects into a pandas DataFrame by flattening the data.

        Args:
            model: The 3Docx source file
            report_type: The report type
            data (List[dataclass]): The list of dataclass objects to be converted.
            depth (int): The maximum depth to flatten the data.

        Returns:
            DataFrame: The flattened data as a pandas DataFrame.

        Examples:
            >>> data = [DataClass(a=1, b=2), DataClass(a=3, b=4)]
            >>> element_to_dataframe(data, depth=2)
               a  b
            0  1  2
            1  3  4
        """

        flattened_data = [flatten_data(obj, max_depth=depth) for obj in data]
        data_frame = pd.DataFrame(flattened_data)
        return ReportDataFrame(
            source=model,
            type=report_type,
            count=data_frame.shape[0],
            unique=data_frame.shape[0],
            elements=data_frame
        )


class OcxObserver(IObserver, ABC):
    """OCX reporter observer class

        event (ObservableEvent): The event that triggered the update.
        payload (Dict): The payload associated with the event.

        Returns:
            None

    """

    def __init__(self, observable: OcxNotifyParser):
        observable.subscribe(self)
        self._ocx_objects = defaultdict(list)
        self._parser = observable

    def update(self, event: ObservableEvent, payload: Dict):
        self._ocx_objects[payload.get('name')].append(payload.get('object'))

    def element_count(self, model: str) -> ReportElementCount:
        """
        Return the 3Docx element count report.

        Returns:
            The report dataclass

        """
        return OcxReportFactory.element_count(model=model, objects=self._ocx_objects)

    def header(self, model: str) -> OcxHeader:
        """
        Return the 3Docx header data.

        Returns:
            The header dataclass

        """
        return OcxReportFactory.create_header(root=self.get_root(), ocx_model=model)

    def get_number_of_elements(self) -> int:
        """
        Returns the number of elements in the parsed 3Docx model.

        Returns:
            int: The number of elements.
        """

        return len(self._ocx_objects)

    def get_root(self) -> Element:
        """
        Returns the root element of the XML document.

        Returns:
            Element: The root element of the XML document.
        """
        return self._parser.get_root()


def get_guid(element: Element) -> Union[None, str]:
    """
    Return the ocx:GUIDRef.
    Args:
        element: The element instance

    Returns:
        The GUIDRef value if present, else None
    """
    guid = None
    attributes = element.attrib
    prefix = element.prefix
    ns = LxmlElement.namespaces_decorate(element.nsmap.get(prefix))
    if is_substring_in_list('GUIDRef', attributes.keys()) and not is_substring_in_list('refType', attributes.keys()):
        guid = attributes.get(f'{ns}GUIDRef')
    return guid


def get_guid_ref(element: Element) -> Union[None, str]:
    """
    Return the guid or localref refernce of an element.
    Args:
        element: The element instance

    Returns:
        The GUIDRef value if present, else None
    """
    guid_ref = None
    attributes = element.attrib
    prefix = element.prefix
    ns = element.nsmap[prefix]
    ns = LxmlElement.namespaces_decorate(ns)
    if is_substring_in_list('refType', attributes.keys()):
        guid_ref = attributes.get(f'{ns}GUIDRef')
    return guid_ref


class OcxReporter:
    """3Docx attribute reporter"""

    def __init__(self):
        self._root = None

    def parse_model(self, model: str) -> Element:
        """
        Parse the 3Docx model and return the root Element.

        Args;
            model: The 3Docx source file

        Returns:
            The XML root element after parsing.
        """
        try:
            file = Path(SourceValidator.validate(model))
            tree = lxml.etree.parse(file)
            self._root = tree.getroot()
            return self._root
        except lxml.etree.XMLSyntaxError as e:
            logger.error(e)
            raise ReporterError(e) from e
        except lxml.etree.LxmlError as e:
            logger.error(e)
            raise ReporterError(e) from e
        except SourceError as e:
            logger.error(e)
            raise ReporterError(e) from e

    def get_root(self) -> Element:
        """Return the XML model root."""
        return self._root

    def get_header(self) -> OcxHeader:
        """
        Returns the header of the OCX report.

        Returns:
            OcxHeader: The header of the OCX report.
        """
        return OcxReportFactory.create_header(self._root)

    def element_count(self, selection: Union[List, str] = "All") -> List:
        """
        Return the count of a list of OCX elements in a model.

        Args:
            selection: Only count elements in the selection list. An empty list will count all elements.
        """
        elements = []
        for element in LxmlElement.iter((self.get_root())):
            elements.append(element.tag)
        sorted_items = sorted(elements)
        grouped_items = [(key, len(group)) for key, group in groupby(sorted_items)]
        return OcxReportFactory.element_count(elements=grouped_items)

    @staticmethod
    def dataframe(model: str, ocx_type: ReportType, depth: int = float('inf')) -> Union[None, ReportDataFrame]:
        """

        Args:
            depth: Flatten the 3Docx dataclass to the depth level. ``inf`` flattens to the deepest level.
            model: The 3Docx source
            ocx_type: The 3Docx type to parse

        Returns:
            The flattened dataframe of tha parsed 3Docx elements
        """
        parser = XmlParser(handler=LxmlEventHandler)
        try:
            file = SourceValidator.validate(model)
            tree = lxml.etree.parse(file)
            root = tree.getroot()
            version = OcxVersion.get_version(file)
            declaration = DeclarationOfOcxImport("ocx", version)
            data_class = DynamicLoader.import_class(declaration, ocx_type.value)
            result = []
            for e in LxmlElement.find_all_children_with_name(root, ocx_type.value):
                ocx_element = parser.parse(e, data_class)
                result.append(ocx_element)
            if result:
                return OcxReportFactory.element_to_dataframe(data=result,
                                                             model=model,
                                                             report_type=ocx_type,
                                                             depth=depth)
            else:
                return None
        except DynamicLoaderError as e:
            logger.error(e)
            raise ReporterError(e) from e
        except SourceError as e:
            logger.error(e)
            raise ReporterError(e) from e
        except ParserError as e:
            logger.error(e)
            raise ReporterError(e) from e
