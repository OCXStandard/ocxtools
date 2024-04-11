#  Copyright (c) 2023-2024. OCX Consortium https://3docx.org. See the LICENSE
"""OCX reporter module"""

# System imports
from collections import defaultdict
from dataclasses import dataclass, is_dataclass
from enum import Enum
from itertools import groupby
from pathlib import Path
from typing import Any, Dict, List, Union

import arrow
# Third party
import lxml
import pandas as pd
from loguru import logger
from lxml.etree import Element, QName
from ocx_schema_parser.xelement import LxmlElement
from xsdata.exceptions import ParserError
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.handlers import LxmlEventHandler

from ocxtools.dataclass.dataclasses import (ElementCount, OcxHeader,
                                            ReportDataFrame,
                                            ReportElementCount, ReportType)
from ocxtools.exceptions import ReporterError, SourceError
from ocxtools.interfaces.interfaces import ABC, IObserver, ObservableEvent
from ocxtools.loader.loader import (DeclarationOfOcxImport, DynamicLoader,
                                    DynamicLoaderError)
# project imports
from ocxtools.parser.parser import OcxNotifyParser
from ocxtools.utils.utilities import (OcxVersion, SourceValidator,
                                      is_substring_in_list)


def all_empty_array(column: pd.Series) -> bool:
    """
    Check if all elements in a column are empty arrays.

    Args:
        column: A pandas Series representing a column of data.

    Returns:
        bool: True if all elements in the column are empty arrays, False otherwise.

    """
    if column.dtype == object and not column.isna().any():
        lengths = column.apply(len)
        if lengths.max() == 0:
            return True
    return False


def flatten_data(data: Any, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flattens nested data structures into a dictionary.

    Args:
        data (Any): The data to be flattened.
        parent_key (str): The parent key to be prepended to the flattened keys. Defaults to an empty string.
        sep (str): The separator to use between keys. Defaults to '.'.

    Returns:
        Dict[str, Any]: The flattened data as a dictionary.

    Examples:
        >>> data = {'a': {'b': {'c': 1}}, 'd': [2, 3]}
        >>> flatten_data(data)
        {'a.b.c': 1, 'd': [2, 3]}
    """
    try:
        flat_data = {}
        if is_dataclass(data):
            data = data.__dict__
        for key, value in data.items():
            if is_dataclass(value):
                value = value.__dict__
            if isinstance(value, Enum):
                value = value.value  # Convert Enum instance to its value
                if not isinstance(value, str):  # If the Enum value is not a string, it is a QName.text
                    value = value.text
            if isinstance(value, dict):
                flat_data |= flatten_data(value, parent_key + key + sep)
            elif isinstance(value, list):
                if all(isinstance(item, (int, float, str)) for item in value):
                    flat_data[parent_key + key] = value
                else:
                    for i, item in enumerate(value):
                        flat_data.update(flatten_data(item, f"{parent_key}{key}-{i}{sep}"))
            else:
                flat_data[parent_key + key] = value
        return flat_data
    except ValueError as e:
        logger.error(e)
        raise ReporterError(e) from e


def duplicate_values(df: pd.DataFrame, col_name: str) -> List:
    """
    Find duplicates in a dataframe column.
    Args:
        df: DatFrame
        col_name: The specified column.

    Returns:

    """
    return df[df.duplicated(col_name)] if col_name in df.columns else []


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
            type=ReportType.HEADER
        )

    @staticmethod
    def element_count_2(model: str, objects: List) -> ReportElementCount:
        """
        Element count report.
        Args:
            model: The source XML file
            objects: List of tuples (tag, count) of 3Docx objects.

        Returns:
            The element count report.
        """
        try:
            elements = [ElementCount(namespace=QName(key).namespace, name=LxmlElement.strip_namespace_tag(key),
                                     count=count) for key, count in objects]
            return ReportElementCount(
                source=model,
                elements=elements,
                count=sum(element.count for element in elements),
                unique=len(elements),
                type=ReportType.COUNT
            )
        except TypeError as e:
            logger.error(f'{e}')
            raise ReporterError(e) from e

    @staticmethod
    def element_count(model: str, objects: List) -> ReportElementCount:
        """
        Element count report
        Args:
            model: The source XML file
            objects: List of tuples (tag, count) of 3Docx objects.

        Returns:
            The element count report.
        """
        try:
            elements = [ElementCount(namespace=QName(key).namespace, name=LxmlElement.strip_namespace_tag(key),
                                     count=count) for key, count in objects]
            return ReportElementCount(
                source=model,
                elements=elements,
                count=sum(element.count for element in elements),
                unique=len(elements),
                type=ReportType.COUNT
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
    def element_to_dataframe(model: str, report_type: ReportType, data: List[dataclass]) -> ReportDataFrame:
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
        try:
            # create a flattened dict from all dataclasses
            flattened_data = [flatten_data(obj) for obj in data]
            data_frame = pd.DataFrame(flattened_data)
            # Drop columns with only empty lists
            # Find columns to drop
            logger.debug(f'Dataframe shape before dropped columns: {data_frame.shape}')
            for col in data_frame.columns:
                if all_empty_array(data_frame[col]):
                    data_frame.drop(col, axis=1, inplace=True)
            logger.debug(f'Dataframe shape after dropped columns: {data_frame.shape}')
            if 'guidref' in data_frame.columns:
                df = data_frame.guidref.duplicated()
                duplicates = (df.duplicated is True).sum()
            else:
                duplicates = 0
            if duplicates > 0:
                logger.error(f'There are {duplicates} duplicate GUIDRef for element {report_type}')
            return ReportDataFrame(
                source=model,
                type=report_type,
                count=data_frame.shape[0],
                unique=data_frame.shape[0] - duplicates,
                columns=data_frame.shape[1],
                levels=max(col.count('.') for col in data_frame.columns),
                elements=data_frame,
            )
        except (IndexError, ValueError) as e:
            logger.error(e)
            raise ReporterError(e) from e

    @staticmethod
    def datframe_types(model: str, report_type: ReportType, data: List[dataclass]) -> ReportDataFrame:
        pass


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

    def get_elements(self) -> Dict:
        """
        Return all parsed elements.

        Returns:
            Dict of all OCX objects from the parsed XML document.
        """
        return self._ocx_objects


def get_guid(element: Element) -> Union[None, str]:
    """
    Return the ocx:GUIDRef.
    Args:
        element: The element instance

    Returns:
        The GUIDRef value if present, else None
    """
    attributes = element.attrib
    prefix = element.prefix
    ns = LxmlElement.namespaces_decorate(element.nsmap.get(prefix))
    return (
        attributes.get(f'{ns}GUIDRef')
        if is_substring_in_list('GUIDRef', attributes.keys())
        and not is_substring_in_list('refType', attributes.keys())
        else None
    )


def get_guid_ref(element: Element) -> Union[None, str]:
    """
    Return the guid or localref refernce of an element.
    Args:
        element: The element instance

    Returns:
        The GUIDRef value if present, else None
    """
    attributes = element.attrib
    prefix = element.prefix
    ns = element.nsmap[prefix]
    ns = LxmlElement.namespaces_decorate(ns)
    return (
        attributes.get(f'{ns}GUIDRef')
        if is_substring_in_list('refType', attributes.keys())
        else None
    )


class OcxReporter:
    """3Docx attribute reporter"""

    def __init__(self):
        self._root = None
        self._model = ''

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
            self._model = model
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

    def get_model(self) -> str:
        """Return the path to the parsed model"""
        return self._model

    def get_header(self) -> OcxHeader:
        """
        Returns the header of the OCX report.

        Returns:
            OcxHeader: The header of the OCX report.
        """
        return OcxReportFactory.create_header(self._root)

    @staticmethod
    def element_count_2(model: str) -> ReportElementCount:
        """
        Return the count of a list of OCX elements in a model.
        This method is slow due to the OcxNotifyParser. Don't use.

        Args:
            model: The 3Docx model source
        """
        try:
            xml_file = SourceValidator.validate(model)
            parser = OcxNotifyParser()
            observer = OcxObserver(observable=parser)
            parser.parse(xml_file)
            elements = observer.get_elements()
            grouped_items = [(k, len(g)) for k, g in sorted(elements.items(), key=lambda k: k)]
            return OcxReportFactory.element_count_2(model=model, objects=grouped_items)
        except (ParserError, SourceError) as e:
            logger.error(e)
            raise ReporterError(e) from e

    def element_count(self, selection: Union[List, str] = "All") -> ReportElementCount:

        elements = [element.tag for element in LxmlElement.iter((self.get_root()))]
        sorted_items = sorted(elements)
        grouped_items = [(k, len(list(g))) for k, g in groupby(sorted_items)]
        return OcxReportFactory.element_count(model=self.get_model(), objects=grouped_items)

    @staticmethod
    def dataframe(model: str, ocx_type: ReportType) -> Union[None, ReportDataFrame]:
        """

        Args:
            model: The 3Docx source
            ocx_type: The 3Docx type to parse

        Returns:
            The dataclass ReportDatFrame containing the flattened data frame of the parsed OCX element
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
            logger.info(f'Parsing object {data_class!r}')
            if ocx_type == ReportType.OCX:
                ocx_element = parser.parse(root, data_class)
                result.append(ocx_element)
            else:
                for e in LxmlElement.find_all_children_with_name(root, ocx_type.value):
                    ocx_element = parser.parse(e, data_class)
                    result.append(ocx_element)
                    logger.info(f'Created report {ocx_type.value!r}')
            if result:
                return OcxReportFactory.element_to_dataframe(data=result,
                                                             model=model,
                                                             report_type=ocx_type)
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
            logger.warning(f'Skipping parsing of {data_class}')
            raise ReporterError(e) from e
