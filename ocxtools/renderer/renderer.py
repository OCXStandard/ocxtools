#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
""" Render classes"""

# System imports
from typing import Dict

# Third party imports
from tabulate import tabulate

# Project imports


class TableRender:
    @staticmethod
    def render(data: Dict):
        """

        Args:
            data:

        Returns:

        """
        headers = []
        values = []
        for k, v in data.items():
            headers.append(k)
            values.append(v)
        return tabulate([headers, values], headers="firstrow")
