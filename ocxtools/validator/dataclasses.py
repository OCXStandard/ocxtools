#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""The validation data dataclasses."""

# System imports
from dataclasses import dataclass, field, fields
from typing import Dict



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

    def to_dict(self, exclude: str = None):
        """
            Dictionary of dataclass attributes with ``metadata["header"]`` as keys.
        Args:
            exclude: Exclude the header with the given value. Output all attributes if ``None``.

        Returns:
            The dictionary of the dataclass attributes.
        """
        return {k: v for k, v in self._to_dict().items() if k != exclude}



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



@dataclass
class ValidationInformation(BaseDataClass):
    """Validation Info"""
    domain: str = field(metadata={"header": "Domain"})
    validation_type: str = field(metadata={"header": "Validation type"})
    description: str = field(metadata={"header": "Description"})
