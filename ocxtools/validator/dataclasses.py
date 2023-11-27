#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""The validation data dataclasses."""

# System imports
from dataclasses import dataclass, field, fields
from typing import Dict, List


@dataclass
class BaseDataClass:
    """Base class for OCX dataclasses.

    Each subclass has to implement a field metadata with name `header` for each of its attributes, for example:

        ``name : str = field(metadata={'header': '<User friendly field name>'})``

    """

    def to_dict(self) -> Dict:
        """Output the data class as a dict with field names as keys."""
        my_fields = fields(self)
        return {
            my_fields[i].metadata["header"]: value
            for i, (key, value) in enumerate(self.__dict__.items())
        }


@dataclass
class ValidationInformation(BaseDataClass):
    """Validation information"""

    domain: str
    validation_type: str
    description: str


@dataclass
class ReportError(BaseDataClass):
    description: str = field(default="", metadata={"header": "Description"})
    location: str = field(default="", metadata={"header": "Location"})


@dataclass
class ReportOverview(BaseDataClass):
    profileID: str = field(default="", metadata={"header": "Schema Version"})


@dataclass
class ReportCounters(BaseDataClass):
    nrOfAssertions: int = field(default=0, metadata={"header": "Assertions"})
    nrOfErrors: int = field(default=0, metadata={"header": "Errors"})
    nrOfWarnings: int = field(default=0, metadata={"header": "Warnings"})


@dataclass
class ReportContext(BaseDataClass):
    name: str = field(default="xml", metadata={"header": "Name"})
    mimeType: str = field(default="application/xml", metadata={"header": "Mime Type"})
    embeddingMethod: str = field(default="STRING", metadata={"header": "Embedding"})
    value: str = ""


@dataclass
class ValidationReport(BaseDataClass):
    """Validation Report"""

    date: str = field(metadata={"header": "Date"})
    result: str = field(metadata={"header": "Result"})
    counters: ReportCounters = None
    overview: ReportOverview = None
    context: List[ReportContext] = None
    reports: [ReportError] = None
