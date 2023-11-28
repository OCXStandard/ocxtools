#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""The validator report class."""

#System imports
from typing import Dict
# Third party imports
import arrow
# Project imports
from ocxtools.validator.dataclasses import (ReportError,
                                            ReportWarning,
                                            ReportAssertion,
                                            ReportOverview,
                                            ReportCounters,
                                            ValidationReport
                                            )



class ValidatorReport:
    """Validator report."""
    def __init__(self, source: str):
        self._source = source
        self._report = None

    def create(self, report_data: Dict) -> ValidationReport:
        """
        Crete the report
        Args:
            report_data: The validation result.

        Returns:
            The report dataclass
        """
        errors =[]
        assertions = []
        warnings = []
        counters = ReportCounters(**report_data.get('counters'))
        overview = ReportOverview(**report_data.get('overview'))
        if counters.nrOfErrors > 0:
            for error in report_data.get('reports').get('error'):
                errors.append(ReportError(**error))
        if counters.nrOfAssertions > 0:
            assertions = [ReportAssertion(**item) for item in report_data.get('assertion')]
        if counters.nrOfWarnings > 0:
            warnings = [ReportWarning(**item) for item in report_data.get('warning')]

        return ValidationReport(source=self._source,
                                date=arrow.get(report_data.get("date")).format(),
                                result=report_data.get('result'),
                                counters= counters,
                                errors= errors,
                                warnings=warnings,
                                assertions=assertions)
