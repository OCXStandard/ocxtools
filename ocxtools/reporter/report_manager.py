#  Copyright (c) 2024. OCX Consortium https://3docx.org. See the LICENSE
"""The report manager implementation."""
# System imports
from collections import defaultdict


from typing import Dict


# Third party
# project imports
from ocxtools.dataclass.dataclasses import Report


class OcxReportManager:
    """
    The OCX reporter class.
    """

    def __init__(self):
        self._reports = defaultdict(list)

    def add_report(self, model: str, report: Report):
        """

        Args:
            model:
            report:
        """
        self._reports[model].append(report)

    def get_reports(self) -> Dict:
        """

        Returns:

        """
        return self._reports

    def report_detail(self, model) -> [Report]:
        """

        Args:
            model:

        Returns:

        """
        if model in self._reports.keys():
            return [report.detail() for report in self._reports[model] if report.type != 'OcxHeader']
        else:
            return []

    def report_summary(self):
        """
        Report summary for all models.
        """
        table = []
        for model, reports in self._reports.items():
            table.extend(
                report.summary()
                for report in reports
                if report.type != 'OcxHeader'
            )
        return table

    def report_headers(self):
        """
        Report summary for all models.
        """
        table = []
        for model, reports in self._reports.items():
            table.extend(
                report.to_dict(exclude=['Report'])
                for report in reports
                if report.type == 'OcxHeader'
            )
        return table
