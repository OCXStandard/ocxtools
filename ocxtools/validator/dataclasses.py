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
class ValidationReport(BaseDataClass):
    """Validation Report"""
    validator_name: str = field(metadata={"header": "Validator name"})
    validator_version: str = field(metadata={"header": "Validator version"})
    validation_type: str = field(metadata={"header": "Validation type"})
    source: str = field(metadata={"header": "Source"})
    date: str = field(metadata={"header": "Date"})
    result: str = field(metadata={"header": "Result"})
    errors: int = field(metadata={"header": "Number of errors"})
    warnings: int = field(metadata={"header": "Number of warnings"})
    assertions: int = field(metadata={"header": "Number of assertions"})
    report: str = field(metadata={"header": "Report"})
