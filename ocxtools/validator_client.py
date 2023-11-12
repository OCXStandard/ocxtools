#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""OCX validator client module."""
# System imports
import aiohttp
import asyncio
# 3rd party

# Project
from ocxtools.async_rest_client import AsyncRestClient


class ValidatorRestClient(AsyncRestClient):
    """OCX validator client"""

    def __init__(self, base_url):
        super().__init__(base_url)

    def get_validator_info(self):
        """Retrieve the validator interface information."""
        endpoint = 'rest/api/info'
        return self.fetch_data(endpoint)

    def validate_model(self, model_url: str, domain: str = 'ocx'):
        """Validate a single OCX model providing the file URL

        Args:
            model_url: The model location
            domain: The validator validation domain

        Returns:
            The validator response
        """
        endpoint = f'{domain}/api/validate'
        params = {
            "contentToValidate": model_url,
            "locationAsPath": True,
            "addInputToReport": False,
            "wrapReportDataInCDATA": False,
        }
        return self.post_data(endpoint, params)
