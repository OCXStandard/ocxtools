#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module for server clients."""

# System reports
import json
from abc import ABC, abstractmethod
from enum import Enum
from io import BytesIO
from typing import Dict, List, Tuple, Union

import pycurl
import requests

# Third party
from loguru import logger

# Project imports
from ocxtools.exceptions import CurlClientError, RequestClientError


class RequestType(Enum):
    """
    Enum class for RequestType containing 4 values - GET, POST, PUT, PATCH, DELETE
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class IRestClient(ABC):
    """Abstract IRestClient interface for REST server clients."""

    def __init__(self, base_url: str):
        """

        Args:
            base_url: The server url.

        Parameters:
            _base_url: base url
            _timeout: Timeout in ms
        """
        self._base_url = base_url
        self._timeout = 30

    @abstractmethod
    def api(
        self, request_type: RequestType, endpoint: str, payload: Union[Dict, str] = None
    ) -> json:
        """Abstract api method.
        Arguments:
            request_type: Type of Request.
               Supported Values - GET, POST, PUT, PATCH, DELETE.
               Type - String
            endpoint: API Endpoint. Type - String
            payload: API Request Parameters or Query String.
        """

    @abstractmethod
    def _post_data(self, endpoint: str, payload: Dict) -> Tuple[int, str]:
        """Abstract internal post method"""

    @abstractmethod
    def _get_data(self, endpoint: str) -> Tuple[int, str]:
        """Abstract internal get method"""

    @abstractmethod
    def set_headers(self, headers: Union[Dict, List]):
        """Abstract set headers method"""


class RestClient(IRestClient):
    """
    Request client
    """

    def __init__(self, base_url):
        super().__init__(base_url)
        self._headers = {
            "Accept": "application/xml",
            "Content-Type": "application/json",
        }

    def api(
        self, request_type: RequestType, endpoint: str, payload: Union[Dict, str] = None
    ) -> json:
        """Function to call the API via the pycurl Library

        Arguments:
            request_type: Type of Request.
               Supported Values - GET, POST, PUT, PATCH, DELETE.
               Type - String
            endpoint: API Endpoint. Type - String
            payload: API Request Parameters or Query String.

        Returns
            Response. The response as a JSON
        """
        url = f"{self._base_url}/{endpoint}"
        try:
            match request_type.value:
                case "GET":
                    status_code, response = self._get_data(url)
                case "POST":
                    status_code, response = self._post_data(url, payload)
                case _:
                    raise (RequestClientError("Not implemented"))

            match status_code:
                case 200:
                    return json.loads(response)
                case 201:
                    return json.loads(response)
                case _:  # All other codes
                    msg = f"ERROR from {url} with status code {status_code}.\nResponse: {response}"
                    logger.error(msg)
                    raise RequestClientError(msg)
        except RequestClientError as e:
            raise RequestClientError from e

    def _get_data(self, url: str) -> Tuple[int, str]:
        """
        Get method.

        Args:
            url: The resource url

        Returns:
            The JSON request response.

        Raises:
             RequestException if the status code is not 200.
        """
        try:
            response = requests.get(url)
            return response.status_code, response.text
        except requests.exceptions.HTTPError as errh:
            logger.error(errh)
            raise RequestClientError(errh) from errh
        except requests.exceptions.ConnectionError as errc:
            logger.error(errc)
            raise RequestClientError(errc) from errc
        except requests.exceptions.Timeout as errt:
            logger.error(errt)
            raise RequestClientError(errt) from errt
        except requests.exceptions.RequestException as err:
            logger.error(err)
            raise RequestClientError(err) from err

    def _post_data(self, url: str, data: Dict) -> Tuple[int, str]:
        """
        Post method.
        Args:
            url: the api resource.
            data: The request body.

        Returns:
            The JSON request response.

        Raises:
             RequestException if the status code is not 201.
        """
        try:
            body = json.dumps(data)
            response = requests.post(url, headers=self._headers, json=body)
            return response.status_code, response.text
        except requests.exceptions.HTTPError as errh:
            logger.error(errh)
        except requests.exceptions.ConnectionError as errc:
            logger.error(errc)
        except requests.exceptions.Timeout as errt:
            logger.error(errt)
        except requests.exceptions.RequestException as err:
            logger.error(err)
        finally:
            msg = (
                f"Failed to fetch data from {url}, status code: {response.status_code}"
            )
            logger.error(msg)
            raise RequestClientError(msg)

    def set_headers(self, headers: Dict):
        """
        Set the request headers
        Args:
            headers: The headers declaration
        """
        self._headers = headers


class CurlRestClient(IRestClient):
    """
    cURL client
    """

    def __init__(self, base_url):
        super().__init__(base_url)
        self._headers = ["Accept: application/json", "Content-Type: application/json"]

    def api(
        self, request_type: RequestType, endpoint: str, payload: Union[Dict, str] = None
    ) -> json:
        """Function to call the API via the pycurl Library

        Arguments:
            request_type: Type of Request.
               Supported Values - GET, POST, PUT, PATCH, DELETE.
               Type - String
            endpoint: API Endpoint. Type - String
            payload: API Request Parameters or Query String.

        Returns
            Response. The response as a JSON
        """
        url = f"{self._base_url}/{endpoint}"
        try:
            match request_type.value:
                case "GET":
                    status_code, response = self._get_data(url)
                case "POST":
                    status_code, response = self._post_data(url, payload)
                case _:
                    raise (RequestClientError("Not implemented"))

            match status_code:
                case 200:
                    return json.loads(response)
                case 201:
                    return json.loads(response)
                case _:  # All other codes
                    msg = f"ERROR from {url} with status code {status_code}.\nResponse: {response}"
                    raise CurlClientError(msg)
        except CurlClientError as e:
            raise CurlClientError from e

    def _get_data(self, url: str) -> Tuple[int, str]:
        """
        Get method.

        Args:
            url: The resource endpoint

        Returns:
            The JSON response.

        Raises:
             CurlClientError if the status code is not 200.
        """
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        buffer = BytesIO()
        # Set the headers
        curl.setopt(pycurl.HTTPHEADER, self._headers)
        # Set the write function to store the response in the buffer
        curl.setopt(pycurl.WRITEDATA, buffer)
        try:
            # Perform the request
            curl.perform()
            # Get the response
            response = buffer.getvalue().decode("utf-8")
            status_code = curl.getinfo(pycurl.HTTP_CODE)
            logger.debug(f"Endpoint: {url}. Status code: {status_code}")
            curl.close()
            return status_code, response
        except pycurl.error as e:
            msg = f"Failed to post data to {url}, status code: {status_code}\nResponse: {e}"
            logger.error(msg)
            raise CurlClientError(msg) from e

    def _post_data(self, url: str, payload: Dict) -> Tuple[int, str]:
        """
        cURL Post method.
        Args:
            url: the api url resource.
            payload: The request body.

        Returns:
            The JSON response.

        Raises:
             CurlClientError if the status code is not 201.
        """
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        body = json.dumps(payload)
        buffer = BytesIO()
        # Set the HTTP method to POST
        curl.setopt(pycurl.POST, 1)
        # Set the POST data
        curl.setopt(pycurl.POSTFIELDS, body)
        # Set the headers
        curl.setopt(pycurl.HTTPHEADER, self._headers)
        # Create a BytesIO object to store the header data
        header_buffer = BytesIO()
        # Set the WRITEFUNCTION to write the header data to the BytesIO object
        curl.setopt(pycurl.HEADERFUNCTION, header_buffer.write)
        # Set the write function to store the response in the buffer
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        try:
            # Perform the request
            curl.perform()
            response = buffer.getvalue().decode("utf-8")
            status_code = curl.getinfo(pycurl.HTTP_CODE)
            # Get the header data from the BytesIO object
            # header_data = header_buffer.getvalue().decode("utf-8")
            logger.debug(f"Endpoint: {url}. Status code: {status_code}")
            curl.close()
            return status_code, response
        except pycurl.error as e:
            msg = f"Failed to post data to {url}, status code: {status_code}\nResponse: {e}"
            logger.error(msg)
            raise CurlClientError(msg) from e

    def set_headers(self, headers: List):
        """
        Set the request headers
        Args:
            headers: The headers declaration
        """
        self._headers = headers
