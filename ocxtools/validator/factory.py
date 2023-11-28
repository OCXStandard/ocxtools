#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Factory module for validation dataclasses."""
# System imports
from typing import Dict, List

# Third party imports
import arrow

# Project import
from ocxtools.validator.dataclasses import (
    ReportContext,
    ReportCounters,
    ReportError,
    ReportOverview,
    ValidationInformation,
    ValidationReport,
)


class ValidatorFactory:
    """Factory for creating the validation data classes."""

    @staticmethod
    def create_info_data(data: Dict) -> List[ValidationInformation]:
        """
        The validator information about supported domains and validation types.
        Args:
            data: Input data

        Returns:
            A list of the ValidationInformation objects
        """
        information = []
        print(data)
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

    @staticmethod
    def create_report_data(data: Dict) -> ValidationReport:
        """
        The validator report data.
        Args:
            data: The validator result

        Returns:
            A list of the ValidationReport objects
        """

        context = []
        errors = []
        context_items = data.get("context").get("items")
        reports = data.get("reports").get("error")
        counters = ReportCounters(**data.get("counters"))
        overview = ReportOverview(**data.get("overview"))
        for item in context_items:
            context.append(ReportContext(**item))
        for error in reports:
            errors.append(ReportError(**error))
        return ValidationReport(
            date=arrow.get(data.get("date")).format(),
            result=data.get("result"),
            counters=counters,
            context=context,
            overview=overview,
            reports=errors,
        )
