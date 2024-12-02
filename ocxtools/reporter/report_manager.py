#  Copyright (c) 2024. OCX Consortium https://3docx.org. See the LICENSE
"""The report manager implementation."""
from __future__ import annotations

# System imports
import os
from collections import defaultdict
from typing import Any, Dict, List

# Third party
# project imports
from ocxtools.dataclass.dataclasses import DetailedReport, Report, ReportType


class OcxReportManager:
    """
    The OCX reporter class.
    """

    def __init__(self):
        self._reports = defaultdict(list)

    def add_report(self, report: Report):
        """
        Add a new report.
        Args:
            report: The report to add
        """
        if report.type.value in self._reports:
            for existing in self.get_report(report.type):
                if os.path.normpath(existing.source) == os.path.normpath(report.source):
                    self._reports[report.type.value].remove(existing)
        self._reports[report.type.value].append(report)

    def delete_report(self, model: str) -> int:
        """
        Delete all reports for the source ``model``
        Args:
            model: The model reports to be deleted
        """
        count = 0
        for report_type, reports in self._reports.items():
            for report in reports:
                if os.path.normpath(report.source) == os.path.normpath(model):
                    self._reports[report_type].remove(report)
                    count += 1
        return count

    def get_report(self, report_type: ReportType) -> List[Report]:
        """
        Return the list of reports of ``report_type``
        Args:
            report_type: The report type
        """
        if report_type.value in self._reports:
            return self._reports[report_type.value]
        else:
            return []

    def get_all_reports(self) -> Dict:
        """
        Retrieve all available reports.

        Returns:
            All reports
        """
        return self._reports

    def has_report(self, report_type: ReportType.value) -> bool:
        """
        Check if a report of a specific type is available.

        Args:
            report_type: The type of report to check for.

        Returns:
            bool: True if a report of the specified type is available, False otherwise.
        """
        return report_type in self._reports.keys() or (report_type == ReportType.ALL.value and len(self._reports) > 0)

    def report_detail(self, report_type: ReportType,
                      level: int = 0,
                      max_col: int = 8,
                      guid: str = '',
                      member: str = 'All') -> List[DetailedReport]:
        """
        Return the detailed reports of ``report_type``
        Args:
            member: Only include columns matching the OCX member. If member='All', include all columns.
            level: Create the report with all elements from level zero to ``level``.
            max_col: Include table columns up to ``max_col``. Default is to 8 columns.
            report_type: The report type

        Returns:
            The list of reports of ``report_type``.
        """
        if report_type.value in self._reports.keys():
            return [report.detail(level=level, member=member, max_col=max_col, guid=guid)
                    for report in self._reports[report_type.value] if report.type != ReportType.HEADER.value]
        else:
            return []

    def report_tree(self, report_type: ReportType) -> list[Any] | dict[Any, Any]:
        if report_type.value in self._reports.keys():
            return [report.tree()
                    for report in self._reports[report_type.value]]
        else:
            return {}

    def report_summary(self) -> List:
        """
        Report summary for all reports.
        """
        tables = []
        for report_type, reports in self._reports.items():
            tables.extend(
                report.summary().to_dict()
                for report in reports
            )
        return tables

    def report_headers(self):
        """
        Return the header information of all parsed models.
        """
        table = []
        for report_type, reports in self._reports.items():
            table.extend(
                report.to_dict(exclude=['Report'])
                for report in reports
                if report.type.value == ReportType.HEADER.value
            )
        return table
