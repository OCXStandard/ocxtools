#  Copyright (c) 2023-2024. OCX Consortium https://3docx.org. See the LICENSE
"""The validation data dataclasses."""

# System imports
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Dict, List, Union
from abc import abstractmethod, ABC
import pandas as pd
import re


# Project imports


class ReportType(Enum):
    """
    Enumeration class representing different types of reports.

    ReportType.ELEMENT_COUNT: Represents a report for element count.
    ReportType.HEADER: Represents a report for OCX header.
    ReportType.SUMMARY: Represents a summary report.
    ReportType.PLATE: Represents a report for plates.
    ReportType.STIFFENER: Represents a report for stiffeners.
    ReportType.BRACKET: Represents a report for brackets.
    ReportType.PILLAR: Represents a report for pillars.
    ReportType.EDGE_REINFORCEMENT: Represents a report for edge reinforcements.
    ReportType.VESSEL: Represents a report for vessels.
    ReportType.PANEL: Represents a report for panels.
    ReportType.COMPARTMENTS: Represents a report for compartments.
    """

    ELEMENT_COUNT = 'ElementCount'
    HEADER = 'OcxHeader'
    SUMMARY = 'Summary'
    PLATE = 'Plate'
    STIFFENER = 'Stiffener'
    BRACKET = 'Bracket'
    PILLAR = 'Pillar'
    EDGE_REINFORCEMENT = 'EdgeReinforcement'
    VESSEL = 'Vessel'
    PANEL = 'Panel'
    COMPARTMENTS = 'Compartments'


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

    def to_dict(self, exclude: List = None) -> Dict:
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
    def summary(self) -> Dict:
        """
        Interface for the Report class
        """
        pass

    @abstractmethod
    def detail(self) -> List:
        """
        Interface for the Report class
        """
        pass


@dataclass
class SummaryReport(BaseDataClass, ABC):
    type: str = field(metadata={"header": "Report"})
    source: str = field(metadata={"header": "Source"})
    count: Union[int, str] = field(metadata={"header": "Count"})
    unique: Union[int, str] = field(metadata={"header": "Unique"})


@dataclass
class OcxHeader(BaseDataClass, Report, ABC):
    """The 3Docx Header information."""
    source: str = field(metadata={"header": "Source"})
    schema_version: str = field(metadata={"header": "Schema Version"})
    namespace: str = field(metadata={"header": "Namespace"})
    time_stamp: str = field(metadata={"header": "Time Stamp"})
    name: str = field(metadata={"header": "Name"})
    author: str = field(metadata={"header": "Author"})
    organization: str = field(metadata={"header": "Organization"})
    originating_system: str = field(metadata={"header": "System"})
    application_version: str = field(metadata={"header": "Version"})
    documentation: str = field(metadata={"header": "Documentation"}, default='')
    type: ReportType = field(metadata={"header": "Report"}, default=ReportType.HEADER)

    def summary(self) -> Dict:
        summary = SummaryReport(source=self.source, type=self.type.value, count='NA', unique='NA')
        return summary.to_dict()

    def detail(self) -> List:
        """
        Detailed missing guid report.
        Returns:
        Returns the list of missing guids.
        """
        return [self.to_dict()]


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
    type: ReportType = field(metadata={"header": "Report"}, default='MissingGuids')

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
    type: ReportType = field(metadata={"header": "Report"}, default='DuplicateGuids')

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


@dataclass
class ElementCount(BaseDataClass, ABC):
    """The element count data."""
    namespace: str = field(metadata={"header": "Namespace"})
    name: str = field(metadata={"header": "Name"})
    count: int = field(metadata={"header": "Count"})


@dataclass
class ReportElementCount(BaseDataClass, Report, ABC):
    """
    Represents a report element count.

    Args:
        source (str): The source of the 3Docx model.
        number_of_elements (int): The number of elements in the report.
        elements (List[ElementCount]): The list of element counts.
        type (str, optional): The type of the report. Defaults to ReportType.ELEMENT_COUNT.

    """

    source: str = field(metadata={"header": "Source"})
    count: int = field(metadata={"header": "Count"})
    unique: int = field(metadata={"header": "Unique Types"})
    elements: List[ElementCount] = field(metadata={"header": "Elements"})
    type: ReportType = field(metadata={"header": "Report"}, default=ReportType.ELEMENT_COUNT)

    def summary(self) -> Dict:
        """
        Element count report summary.

        Returns:
            The summary of the element count report.
        """
        summary = SummaryReport(source=self.source, type=self.type.value, count=self.count, unique=self.unique)
        return summary.to_dict()

    def detail(self) -> List:
        """
        The element count details'
        Returns:
        The detailed element count report
        """
        return [item.to_dict() for item in self.elements]


@dataclass
class ReportDataFrame(BaseDataClass, Report, ABC):
    """
    Represents a Pandas DataFrame report.

    Args:
        source (str): The source of the 3Docx model.
        number_of_elements (int): The number of elements in the report.
        elements (List[ElementCount]): The list of element counts.
        type (str, optional): The type of the report. Defaults to ReportType.ELEMENT_COUNT.

    """

    source: str = field(metadata={"header": "Source"})
    count: int = field(metadata={"header": "Count"})
    unique: int = field(metadata={"header": "Unique Types"})
    elements: pd.DataFrame = field(metadata={"header": "Elements"})
    type: ReportType = field(metadata={"header": "Report"})

    def summary(self) -> Dict:
        """
        TataFrame report summary.

        Returns:
            The summary of the dataframe.
        """
        summary = SummaryReport(source=self.source, type=self.type.value, count=self.count, unique=self.count)
        return summary.to_dict()

    def detail(self) -> List:
        """
        The dataframe content details'
        Returns:
        The detailed dataframe content
        """
        match self.type.value:
            case ReportType.PLATE.value:
                df = self.elements
                # Throw away lower level ids
                columns = df.columns.tolist()
                columns = [id for id in columns if id.count('.') <= 2]
                columns = [
                    id
                    for id in columns
                    if not any(
                        re.search(word, id)
                        for word in [
                            'outer_contour',
                            'inner_contour',
                            'limited_by',
                            'unbounded_geometry',
                            'cut_by',
                        ]
                    )
                ]
                data = df[columns].to_dict(orient='records')
                return data[0] if len(data) == 1 else data
            case _:
                return []
