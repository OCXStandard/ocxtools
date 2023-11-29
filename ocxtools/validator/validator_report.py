#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""The validator report class."""

# System imports
from typing import Dict
# Third party imports
import arrow
import lxml.etree
from loguru import logger
from typing import List
import json
# Project imports

from ocxtools.validator.dataclasses import ValidationReport, ValidationInformation
from ocx_schema_parser.xelement import LxmlElement
from ocxtools.exceptions import ReporterError


class ValidatorReport:
    """Validator report."""

    @staticmethod
    def create_report(source: str, report_data: str) -> ValidationReport:
        """
        Create the report
        Args:
            report_data: The validation result.

        Returns:
            The report dataclass
        """
        try:
            report_bytes = report_data.encode(encoding='utf-8')
            root = lxml.etree.fromstring(report_bytes)
            n_assert = int(LxmlElement.find_child_with_name(root, 'nrOfAssertions').text)
            n_err = int(LxmlElement.find_child_with_name(root, 'nrOfAssertions').text)
            n_warn = int(LxmlElement.find_child_with_name(root, 'nrOfAssertions').text)
            profile_id = LxmlElement.find_child_with_name(root, 'profileID').text
            result = LxmlElement.find_child_with_name(root, 'result').text
            date = LxmlElement.find_child_with_name(root, 'date').text
            validator_name = LxmlElement.find_child_with_name(root, 'validationServiceName').text
            validator_version = LxmlElement.find_child_with_name(root, 'validationServiceVersion').text
            errors = LxmlElement.find_all_children_with_name(root, 'errors')
            return ValidationReport(source=source,
                                    date=arrow.get(date).format(),
                                    result=result,
                                    validation_type=profile_id,
                                    validator_version=validator_version,
                                    validator_name=validator_name,
                                    errors=n_err,
                                    warnings=n_warn,
                                    assertions=n_assert,
                                    report=report_data)
        except ValueError as e:
            logger.error(e)
            raise ReporterError(e) from e
    @staticmethod
    def create_info_data(response: str) -> List[ValidationInformation]:
        """
        The validator information about supported domains and validation types.
        Args:
            response: The input data

        Returns:
            A list of the ValidationInformation objects
        """
        information = []
        data = json.loads(response)
        try:
            for item in data:
                domain = item.get("domain")
                for validations in item.get("validationTypes"):
                    description = validations.get("description")
                    validation_type = validations.get("type")
                    information.append(
                        ValidationInformation(
                            domain=domain,
                            validation_type=validation_type,
                            description=description,
                        )
                    )
            return information
        except ValueError as e:
            logger.error(e)
            raise ReporterError(e) from e
