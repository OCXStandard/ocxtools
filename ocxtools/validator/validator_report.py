#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""The validator report class."""

import json
# System imports
import re
from typing import List

# Third party imports
import arrow
import lxml.etree
from loguru import logger
from ocx_schema_parser.xelement import LxmlElement

from ocxtools.dataclass.dataclasses import (OcxHeader, ValidationDetails,
                                            ValidationInformation,
                                            ValidationReport)
from ocxtools.exceptions import ReporterError

# Project imports



class ValidatorReportFactory:
    """Validator report."""

    @staticmethod
    def create_report(source: str, report_data: str, header: OcxHeader) -> ValidationReport:
        """
        Create the validation report.
        Args:
            source: The source 3Docx model source file name.
            report_data: The validation result.
            header: The 3Docx Header information

        Returns:
            The report dataclass
        """
        try:
            report_bytes = report_data.encode(encoding='utf-8')
            root = lxml.etree.fromstring(report_bytes)
            n_assert = int(LxmlElement.find_child_with_name(root, 'nrOfAssertions').text)
            n_err = int(LxmlElement.find_child_with_name(root, 'nrOfErrors').text)
            n_warn = int(LxmlElement.find_child_with_name(root, 'nrOfWarnings').text)
            profile_id = LxmlElement.find_child_with_name(root, 'profileID').text
            result = LxmlElement.find_child_with_name(root, 'result').text
            date = LxmlElement.find_child_with_name(root, 'date').text
            validator_name = LxmlElement.find_child_with_name(root, 'validationServiceName')
            validator_name = validator_name.text if validator_name is not None else ''
            validator_version = LxmlElement.find_child_with_name(root, 'validationServiceVersion')
            validator_version = validator_version.text if validator_version is not None else ''
            LxmlElement.find_all_children_with_name(root, 'errors')
            # Iterate over error elements and create the detailed report
            errors = []
            for error in LxmlElement.iter(root,'{*}error'):
                description = LxmlElement.find_child_with_name(error, 'description').text
                text = description
                if '{' in description:
                    text = ''
                    sub_str = '"http'
                    start_indices = [i.start() for i in re.finditer(sub_str, description)]
                    sub_str = '":'
                    end_indices = [i.start() for i in re.finditer(sub_str, description)]
                    end_indices = [index + 2 for index in end_indices]
                    slices = map(slice,start_indices,end_indices)
                    for s in slices:
                        text = description.replace(description[s], '')
                    text = text.replace('{', '')
                    text = text.replace('}', '')
                location = LxmlElement.find_child_with_name(error,'location')
                # Define the regex pattern to extract numbers between colons
                pattern = re.compile(r'(?<=:)\d+(?=:|$)')
                # Find all matches in the input string
                matches = pattern.findall(location.text)
                detailed_report = ValidationDetails(description=text, line=matches[0], column=matches[1])
                errors.append(detailed_report)
            return ValidationReport(source=source,
                                    date=arrow.get(date).format(),
                                    result=result,
                                    validation_type=profile_id,
                                    validator_version=validator_version,
                                    validator_name=validator_name,
                                    errors=n_err,
                                    warnings=n_warn,
                                    assertions=n_assert,
                                    report=report_data,
                                    error_details=errors,
                                    warning_details=[],
                                    assertion_details=[],
                                    ocx_header=header)
        except ValueError as e:
            logger.error(e)
            raise ReporterError(e) from e

    @staticmethod
    def create_info_report(response: str) -> List[ValidationInformation]:
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
