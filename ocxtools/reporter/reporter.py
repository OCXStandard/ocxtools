#  Copyright (c) 2023-2024. OCX Consortium https://3docx.org. See the LICENSE
"""OCX reporter module"""

# System imports
from collections import defaultdict
from typing import Dict, List, Union
from pathlib import Path
from dataclasses import dataclass
from itertools import groupby

# Third party
import lxml
from lxml.etree import Element
from loguru import logger
import arrow
# project imports
from ocxtools.parser.parser import OcxNotifyParser
from ocxtools.dataclass.dataclasses import (Guids, OcxHeader, References, ReportDuplicateGuids,
                                            ReportMissingReferences, ElementCount, ReportElementCount)
from ocxtools.interfaces.interfaces import ABC, IObserver, ObservableEvent
from ocxtools.utils.utilities import SourceValidator
from ocxtools.exceptions import ReporterError, SourceError
from ocx_schema_parser.xelement import LxmlElement


def is_substring_in_list(substring, string_list):
    """

    Args:
        substring: The search string
        string_list: List of strings

    Returns:
        True if the substring is found, False otherwise.
    """
    return any(substring in string for string in string_list)


def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten a nested dictionary.

    Parameters:
    - d: The input dictionary to be flattened.
    - parent_key: The parent key used for recursive calls.
    - sep: The separator used to concatenate keys.

    Returns:
    - A flattened dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif not isinstance(v, list):
            items.append((new_key, v))
    return dict(items)


class OcxObserver(IObserver, ABC):
    """OCX reporter observer class"""

    def __init__(self, observable: OcxNotifyParser):
        observable.subscribe(self)
        self._ocx_objects = defaultdict(list)

    def update(self, event: ObservableEvent, payload: Dict):
        self._ocx_objects[payload.get('name')].append(payload.get('object'))

    def element_count(self, selection: Union[List, str] = "All") -> List:
        """
        Return the count of a list of OCX elements in a model.

        Args:
            selection: Only count elements in the selection list. An empty list will count all elements.
        """
        if "All" in selection:
            return [{'Name': LxmlElement.strip_namespace_tag(key),
                     'Count': len(self._ocx_objects[key])} for key in sorted(self._ocx_objects)]
        else:
            return [{'Name': LxmlElement.strip_namespace_tag(key),
                     'Count': len(self._ocx_objects[key])} for key in sorted(self._ocx_objects) if key in selection]


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

    def __init__(self, ocx_model: str):
        self._model = ocx_model
        self._references = defaultdict(list)
        self._elements = defaultdict(list)
        self._ids = defaultdict(list)
        self._root = None
        self._duplicates = defaultdict(list)

    def parse_model(self) -> OcxHeader:
        """
        Parse the 3Docx model and return the Header information.
        """
        try:
            file = Path(SourceValidator.validate(self._model))
            tree = lxml.etree.parse(file)
            self._root = tree.getroot()
            return OcxReportFactory.create_header(self._root, self._model)
        except lxml.etree.XMLSyntaxError as e:
            logger.error(e)
            raise ReporterError(e) from e
        except lxml.etree.LxmlError as e:
            logger.error(e)
            raise ReporterError(e) from e
        except SourceError as e:
            logger.error(e)
            raise ReporterError(e) from e

    def get_model(self) -> str:
        """Return the source model file name."""
        return self._model

    def get_root(self) -> Element:
        """Return the XML model root."""
        return self._root

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

    def check_references(self) -> dataclass:
        """
        Return 3Docx report with any missing references.

        """
        return OcxReportFactory.missing_reference_guids(self._model, references=self._references, ids=self._ids)

    def check_duplicates(self) -> dataclass:
        """
        Return 3Docx report with any missing references.

        """
        return OcxReportFactory.duplicate_guids(self._model, duplicates=self._duplicates)


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
        return OcxHeader(
            source=ocx_model,
            time_stamp=arrow.get(xml_header.get('time_stamp')).format(),
            author=xml_header.get('author'),
            name=xml_header.get('name'),
            originating_system=xml_header.get('originating_system'),
            organization=xml_header.get('organization'),
            application_version=xml_header.get('application_version'),
        )

    @staticmethod
    def duplicate_guids(model: str, duplicates: Dict) -> dataclass:
        """
        Create duplicate guids report.

        Args:
            model: The path to the 3Docx file.
            duplicates: A dictionary of all the duplicate ids in th source model.

        """
        details = []
        errors = len(duplicates)
        for guid in duplicates:
            logger.debug(guid)
            for item in duplicates[guid]:
                details.append(
                    Guids(
                        tag=item.tag,
                        guid=guid,
                        id=item.get('id'),
                        name=item.get('name'),
                        source_line=LxmlElement.get_source_line(item)
                    ))
        return ReportDuplicateGuids(source=model, errors=errors, duplicate_guids=details)

    @staticmethod
    def missing_reference_guids(model: str, references: Dict, ids: Dict) -> dataclass():
        """
        Create missing guid references report.

        Args:
            ids: Table of model ids (id and GuiDref)
            references: A dictionary of all GUIDRef references in the source model.
            model: The path to the 3Docx file.

        Returns:
            The missing references report.

        """
        missing_guids = [e_id for e_id in references.keys() if e_id not in ids.keys()]
        errors = len(missing_guids)
        missing = []
        for ref in missing_guids:
            for item in references[ref]:
                missing.append(
                    References(
                        source=model,
                        tag=item.tag,
                        guid=ref,
                        local_ref=item.get('localRef'),
                        source_line=LxmlElement.get_source_line(item),
                    )
                )
        return ReportMissingReferences(source=model, errors=errors, missing_references=missing)

    @staticmethod
    def element_count(model: str, count: int, groups: List) -> ReportElementCount:
        """
        Element count report
        Args:
            elements: List of tuples (tag, count)

        Returns:
            List of ElementCount dataclasses
        """
        counts = [ElementCount(tag=element[0], count=element[1]) for element in groups]
        return ReportElementCount(source=model, number_of_elements=counts, elements=counts)
