#  Copyright (c) 2023-2024. OCX Consortium https://3docx.org. See the LICENSE
"""The validation data dataclasses."""

# System imports
from dataclasses import dataclass, field, fields
from typing import Dict, List, Union
from abc import abstractmethod, ABC


# Project imports


@dataclass
class BaseDataClass:
    """Base class for OCX dataclasses.

    Each subclass has to implement a field metadata with name `header` for each of its attributes, for example:

        ``name : str = field(metadata={'header': '<User friendly field name>'})``

    """

    def _to_dict(self) -> Dict:
        """Output the data class as a dict with field names as keys.
        Args:

        """
        my_fields = fields(self)
        return {
            my_fields[i].metadata["header"]: value
            for i, (key, value) in enumerate(self.__dict__.items())
        }

    def to_dict(self, exclude: List = None):
        """
            Dictionary of dataclass attributes with ``metadata["header"]`` as keys.
        Args:
            exclude: Exclude all headers in the ``exclude`` list. Output all attributes if ``None``.

        Returns:
            The dictionary of the dataclass attributes.
        """
        if exclude is None:
            exclude = []
        return {k: v for k, v in self._to_dict().items() if k not in exclude}


@dataclass
class Report(ABC):
    """Abstract interface."""
    @abstractmethod
    def summary(self):
        """
        Interface for the Report class
        """
        pass

    @abstractmethod
    def detail(self):
        """
        Interface for the Report class
        """
        pass


@dataclass
class OcxHeader(BaseDataClass):
    """The 3Docx Header information."""
    source: str = field(metadata={"header": "Source"})
    time_stamp: str = field(metadata={"header": "Time Stamp"})
    name: str = field(metadata={"header": "Name"})
    author: str = field(metadata={"header": "Author"})
    organization: str = field(metadata={"header": "Organization"})
    originating_system: str = field(metadata={"header": "System"})
    application_version: str = field(metadata={"header": "Version"})
    documentation: str = field(metadata={"header": "Documentation"}, default='')
    type: str = field(metadata={"header": "OcxHeader"}, default='OcxHeader')


@dataclass
class ValidationDetails(BaseDataClass):
    """Validation Details"""
    description: str = field(metadata={"header": "Description"})
    line: int = field(metadata={"header": "Line"})
    column: int = field(metadata={"header": "Column"})


@dataclass
class ValidationReport(BaseDataClass):
    """Validation Report"""
    source: str = field(metadata={"header": "Source"})
    result: str = field(metadata={"header": "Result"})
    errors: int = field(metadata={"header": "Number of errors"})
    warnings: int = field(metadata={"header": "Number of warnings"})
    assertions: int = field(metadata={"header": "Number of assertions"})
    validator_name: str = field(metadata={"header": "Validator name"})
    validator_version: str = field(metadata={"header": "Validator version"})
    validation_type: str = field(metadata={"header": "Validation type"})
    date: str = field(metadata={"header": "Date"})
    report: str = field(metadata={"header": "Report"})
    error_details: List[ValidationDetails] = field(metadata={"header": "Errors"})
    assertion_details: List[ValidationDetails] = field(metadata={"header": "Assertions"})
    warning_details: List[ValidationDetails] = field(metadata={"header": "Warnings"})
    ocx_header: OcxHeader = field(metadata={"header": "OCX Header"})


@dataclass
class ValidationInformation(BaseDataClass):
    """Validation Info"""
    domain: str = field(metadata={"header": "Domain"})
    validation_type: str = field(metadata={"header": "Validation type"})
    description: str = field(metadata={"header": "Description"})


@dataclass
class ElementCount(BaseDataClass):
    """Element count report details."""
    tag: str = field(metadata={"header": "Tag"})
    count: int = field(metadata={"header": "Count"})


@dataclass
class References(BaseDataClass):
    """The GUIDRef report details."""
    tag: str = field(metadata={"header": "Tag"})
    local_ref: str = field(metadata={"header": "Local Reference"})
    guid: str = field(metadata={"header": "GUID"})
    source_line: int = field(metadata={"header": "Line Number"})


@dataclass
class Guids(BaseDataClass):
    """The GUIDRef report details."""
    tag: str = field(metadata={"header": "Tag"})
    name: str = field(metadata={"header": "Name"})
    id: str = field(metadata={"header": "Id"})
    guid: str = field(metadata={"header": "GUID"})
    source_line: int = field(metadata={"header": "Line Number"})


@dataclass
class ReportMissingReferences(BaseDataClass, Report, ABC):
    """The content report data."""
    source: str = field(metadata={"header": "Source"})
    errors: int = field(metadata={"header": "Number"})
    missing_references: List[Guids] = field(metadata={"header": "Missing"})
    type: str = field(metadata={"header": "Report"}, default='MissingGuids')

    def summary(self) -> Dict:
        return self.to_dict(exclude=['Missing'])

    def detail(self) -> Union[None, List]:
        """
        Detailed missing guid report.
        Returns:
        Returns the list of missing guids.
        """
        if len(self.missing_references) > 0:
            return [missing.to_dict() for missing in self.missing_references]
        else:
            return None


@dataclass
class ReportDuplicateGuids(BaseDataClass, Report, ABC):
    """The content report data."""
    source: str = field(metadata={"header": "Source"})
    errors: int = field(metadata={"header": "Number"})
    duplicate_guids: List[Guids] = field(metadata={"header": "Duplicates"})
    type: str = field(metadata={"header": "Report"}, default='DuplicateGuids')

    def summary(self) -> Dict:
        return self.to_dict(exclude=['Duplicates'])

    def detail(self) -> Union[None, List]:
        """
        Detailed missing guid report.
        Returns:
        Returns the list of missing guids or None if .
        """
        if len(self.duplicate_guids) > 0:
            return [duplicate.to_dict() for duplicate in self.duplicate_guids]
        else:
            return None


class ReportElementCount(BaseDataClass, Report, ABC):
    """The element count report data."""
    source: str = field(metadata={"header": "Source"})
    number_of_elements: int = field(metadata={"header": "Number"})
    elements: List[ElementCount] = field(metadata={"header": "Elements"})
    type: str = field(metadata={"header": "Report"}, default='ElementCount')

    def summary(self) -> Dict:
        return self.to_dict(exlude=['Elements'])

    def details(self) -> List:
        """
        The element count details
        Returns:

        """
        return [item.to_dict() for item in self.elements]
