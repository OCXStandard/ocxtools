#  Copyright (c) 2023-2024. OCX Consortium https://3docx.org. See the LICENSE
"""The validation data dataclasses."""

from abc import ABC
from collections import defaultdict
# System imports
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Dict, List, Union

import pandas as pd
# Third party imports
from xsdata.utils.text import snake_case

# Project imports
from ocxtools.exceptions import ReporterError


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

    OCX = 'OcxXml'
    VESSEL = 'Vessel'
    HEADER = 'Header'
    PLATE = 'Plate'
    STIFFENER = 'Stiffener'
    BRACKET = 'Bracket'
    PILLAR = 'Pillar'
    EDGE_REINFORCEMENT = 'EdgeReinforcement'
    PARTICULARS = 'PrincipalParticulars'
    PANEL = 'Panel'
    COMPARTMENT = 'Compartment'
    PHYSICAL_SPACE = 'PhysicalSpace'
    DESIGN_VIEW = 'DesignView'
    COORDINATE_SYSTEM = 'CoordinateSystem'
    UNIT = 'Unit'
    MATERIAL_CATALOGUE = 'MaterialCatalogue'
    SECTION_CATALOGUE = 'XsectionCatalogue'
    HOLE_CATALOGUE = 'HoleShapeCatalogue'
    COUNT = 'ElementCount'  # Count of elements in the 3Docx file
    ALL = "All"  # Use "All" to include all report types.


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

    type: ReportType = field(metadata={"header": "Report"})

    def __eq__(self, other):
        return self.type == other.type if isinstance(other, self.__class__) else False


@dataclass
class SummaryReport(BaseDataClass, ABC):
    """
    Summary:
        Represents a summary report with basic attributes.

    Explanation:
        This class represents a summary report and provides attributes to store basic information about the report.
        It includes the type of the report, its source, the number of columns in the table,
        the levels of the table, the count of items, and the count of unique items.
        The class inherits from the `BaseDataClass` class and is designed to be used as a base class for other report
        classes.

    Args:
        type (str): The type of the report.
        source (str): The source of the report.
        columns (int): The number of columns in the table.
        levels (Union[int, str]): The levels of the table.
        count (Union[int, str]): The count of items.
        unique (Union[int, str]): The count of unique items.

    Returns:
        None

    """

    type: str = field(metadata={"header": "Report"})
    source: str = field(metadata={"header": "Source"})
    columns: int = field(metadata={"header": "Table Columns"})
    levels: Union[int, str] = field(metadata={"header": "Table levels"})
    count: Union[int, str] = field(metadata={"header": "Items"})
    unique: Union[int, str] = field(metadata={"header": "Unique Items"})


@dataclass
class DetailedReport(SummaryReport):
    """
        Summary:
            Represents a detailed report with additional content.

        Explanation:
            This class extends the `SummaryReport` class and represents a detailed report.
            It includes all the attributes of the `SummaryReport` class, as well as an additional attribute called
            `content`. The `content` attribute stores a list of dictionaries representing the detailed content of
            the report.

        Args:
            content (List[Dict]): The detailed content of the report.

        Returns:
            None

    """

    content: List[Dict] = field(metadata={"header": "Content"})


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
        count (int): The number of elements in the report.
        elements (List[ElementCount]): The list of element counts.
        type (str, optional): The type of the report. Defaults to ReportType.ELEMENT_COUNT.

    """

    source: str = field(metadata={"header": "Source"})
    count: int = field(metadata={"header": "Count"})
    unique: int = field(metadata={"header": "Unique Types"})
    elements: List[ElementCount] = field(metadata={"header": "Elements"})
    type: ReportType = field(metadata={"header": "Report"})

    def summary(self) -> SummaryReport:
        """
        Element count report summary.

        Returns:
            The summary of the element count report.
        """
        return SummaryReport(source=self.source, type=self.type.value, count=self.count, levels=1,
                             unique=self.unique, columns=3)

    def detail(self, level: int, member: str, max_col: int, guid: str = '') -> DetailedReport:
        """
        The element count details'
        Returns:
        The detailed element count report
        """
        table = []
        if member.lower() == 'all':
            table = [item.to_dict() for item in self.elements]
        else:
            table.extend(
                item.to_dict()
                for item in self.elements
                if item.to_dict().get('Name') == member
            )
        summary = self.summary()
        return DetailedReport(**summary.__dict__, content=table)


@dataclass
class ReportDataFrame(Report, BaseDataClass, ABC):
    """
    Represents a Pandas DataFrame report.

    Args:
        source (str): The source of the 3Docx model.
        count (int): The number of elements in the report.
        unique(int): The number of elements with unique GUIDs
        elements (List[ElementCount]): The list of element counts.
        type (str, optional): The type of the report. Defaults to ReportType.ELEMENT_COUNT.

    """

    source: str = field(metadata={"header": "Source"})
    count: int = field(metadata={"header": "Count"})
    unique: int = field(metadata={"header": "Unique Types"})
    columns: int = field(metadata={"header": "Columns"})
    levels: int = field(metadata={"header": "Levels"})
    elements: pd.DataFrame = field(metadata={"header": "Elements"})
    type: ReportType = field(metadata={"header": "Report"})

    def summary(self) -> SummaryReport:
        """
        DataFrame report summary.

        Returns:
            The summary of the dataframe.
        """
        return SummaryReport(source=self.source, type=self.type.value, count=self.count, unique=self.unique,
                             columns=self.columns, levels=self.levels)

    def detail(self, level: int, member: str, max_col: int, guid: str = '') -> DetailedReport:
        """
        Summary:
            Generates a detailed report based on specified criteria.

        Explanation:
            This function generates a detailed report by filtering and selecting columns from the existing report.
            It takes in the level of detail, the member to filter on, the maximum number of columns to include in the detailed report,
            and an optional GUID to further filter the report content.
            The function filters the columns based on the member and level criteria, and then extracts the content of the filtered columns.
            If a GUID is provided, it filters the report content based on the matching GUID.
            The function also includes the summary information from the original report.
            It returns a `DetailedReport` instance with the extracted content and summary information.

        Args:
            level (int): The level of detail for the report.
            member (str): The member to filter on. Use 'all' to include all columns.
            max_col (int): The maximum number of columns to include in the detailed report.
            guid (str, optional): The GUID to filter the report content. Defaults to ''.

        Returns:
            DetailedReport: A detailed report instance with the extracted content and summary information.

        Raises:
            ReporterError: If the specified member is not found in the report or if no matching GUID is found.

        Examples:
            N/A
        """

        df = self.elements
        # Report content matching guid
        if guid != '' and 'guidref' in df.columns:
            mask = df['guidref'].isin([guid])
            if mask is None:
                raise ReporterError(f'No matching GUIDref for objects of type {self.type!r}')
            else:
                df = df[mask]
        # Filter on columns matching member and ignore levels
        if member.lower() != 'all':
            pattern = f'^{snake_case(member)}-*'
            columns = df.filter(regex=pattern)
            if columns.empty:
                raise ReporterError(f'No OCX subtype {member!r} in report {self.type.value!r}')
        else:
            columns = df.columns.tolist()
            columns = [col_id for col_id in columns if col_id.count('.') <= level]
        max_col = min(max_col, len(columns))
        content = df[columns].iloc[:, 0:max_col].to_dict(orient='records')
        summary = self.summary()
        return DetailedReport(**summary.__dict__, content=content)

    def tree(self) -> Dict:
        """
        Returns a dictionary representing the tree structure of the elements.

        Returns:
            Dict: A dictionary where the keys are the levels of the tree and the values are lists of columns at each level.
        """
        tree = {}
        for column in self.elements.columns:
            levels = column.split('.')
            current_level = tree
            for level in levels:
                if level not in current_level:
                    current_level[level] = {}
                current_level = current_level[level]
        return tree


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

    def summary(self) -> SummaryReport:
        return SummaryReport(source=self.source, type=self.type.value, count='NA', unique='NA', levels=1)

    def detail(self, number_of_columns: int) -> DetailedReport:
        """
        Detailed missing guid report.
        Returns:
        Returns the list of missing guids.
        """
        return DetailedReport(**self.summary().__dict__, content=[])

    def tree(self) -> Dict:
        tree = defaultdict(list)
        for column in self.to_dict(exclude=['Report']):
            tree['level_0'].append(column)
        return tree


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
