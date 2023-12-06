#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""OCX validator client module."""
# System imports
from pathlib import Path
import base64
import json
from abc import ABC
from enum import Enum
from collections import defaultdict
from typing import List
import itertools

import pycurl
from requests.exceptions import ConnectionError
from typing import Dict
# 3rd party imports
import lxml.etree
from loguru import logger

# Project
from ocxtools.clients.clients import CurlClientError, CurlRestClient, RestClient, RequestClientError, RequestType
from ocxtools.exceptions import SourceError
from ocxtools.utils.utilities import OcxVersion, SourceValidator
from ocxtools.validator.validator_report import ValidatorReport


class EmbeddingMethod(Enum):
    """Embedding type."""

    STRING = "STRING"
    URL = "URL"
    BASE64 = "BASE64"


class OcxValidatorCurlClient(CurlRestClient, ABC):
    """OCX validator cURL client"""

    def __init__(self, base_url, service_endpoint: str = "rest/api/info"):
        super().__init__(base_url)
        self._get_endpoint = service_endpoint
        self._validation_types = defaultdict(list)
        try:
            response = self.get_validator_info()
            report = ValidatorReport.create_info_data(response)
            for info in report:
                self._validation_types[info.domain].append(info.validation_type)
        except RequestClientError as e:
            msg = f'The validator service {base_url} is not running: {e}'
            logger.error(msg)
            raise ValidatorError(msg).with_traceback(None) from None
        except CurlClientError as e:
            logger.error(e)
            raise ValidatorError(e).with_traceback(None) from None

    def get_validator_info(self) -> json:
        """Retrieve the OCX docker validator interface information."""
        endpoint = self._get_endpoint
        self.set_headers({"Accept": "application/json"})
        return self.api(request_type=RequestType.GET, endpoint=endpoint)

    def _validate(
            self,
            content: str,
            domain: str,
            validation_type: str,
            embedding_method: str,
            location_as_path: bool,
            add_input_to_report: bool = True,
            wrap_report_data_in_cdata: bool = False,
            locale: str = "en",
    ) -> json:
        """Internal method. Validate a single OCX model.

        Args:
            wrap_report_data_in_cdata:
            add_input_to_report: If True, add the input source to the report. Default = ``True``
            location_as_path: True if embedding method is set to ``URL``
            validation_type: The validation type
            embedding_method: The content embedding. Valid values: ``STRING``, ``URL``, ``BASE64``
            content: The content to be embedded
            domain: The validator validation domain
            locale: The validator language setting.

        Returns:
            The validator response
        Raises:
            A ValidatorError if failing.
        """
        # Verify that the validation type is available
        if validation_type in self.get_validation_types():
            params = {
                "contentToValidate": content,
                "embeddingMethod": embedding_method,
                "validationType": validation_type,
                "locationAsPath": location_as_path,
                "addInputToReport": add_input_to_report,
                "wrapReportDataInCDATA": wrap_report_data_in_cdata,
                "locale": locale,
            }
            self.set_headers({"accept": "application/xml", "Content-Type": "application/json"})
            endpoint = f"rest/{domain}/api/validate"
            return self.api(
                request_type=RequestType.POST, endpoint=endpoint, payload=params
            )
        else:
            raise ValidatorError(f'The validation type {validation_type!r} is invalid. '
                                 f'Valid validations: {self.get_validation_types()}. '
                                 'Try validate to one of the available types')

    def validate_one(
            self,
            ocx_model: str,
            domain: str = "ocx",
            schema_version: str = '3.0.0',
            embedding_method: EmbeddingMethod = EmbeddingMethod.BASE64, force_version: bool = False) -> str:
        """Validate a single 3Docx XML file. The XML file will be pretty-print formatted before validation.

        Args:
            ocx_model: The model source path
            domain: The validator validation domain
            schema_version: Schema version to use in the validation
            force_version: True if ``version`` shall be used irrespective of the source 3Docx version            embedding_method: The content embedding method.
            embedding_method: The source embedding method. Valid Types are ``STRING`` or ``BASE64``.

        Returns:
            The validator response as xml or json string

        Raises:
            ValidatorError on a bad response.
        """
        try:
            Path(SourceValidator.validate(ocx_model))
            version = OcxVersion.get_version(ocx_model)
            if force_version:
                version = schema_version
            validation_type = f"{domain}.v{version}"
            tree = lxml.etree.parse(ocx_model)
            byte_string = lxml.etree.tostring(tree)
            decoded_string = byte_string.decode("utf-8")
            match embedding_method.value:
                case "BASE64":
                    base64_bytes = base64.b64encode(byte_string)
                    content = base64_bytes.decode("utf-8")
                    location_as_path = False
                case "STRING":
                    content = decoded_string
                    location_as_path = False
                case _:
                    raise ValidatorError(
                        f'Embedding method {embedding_method.value!r} is not supported.'
                    )
            return self._validate(
                content,
                domain,
                validation_type,
                embedding_method.value,
                location_as_path,
            )
        except lxml.etree.XMLSyntaxError as e:
            logger.error(e)
            raise ValidatorError(e) from e
        except lxml.etree.LxmlError as e:
            logger.error(e)
            raise ValidatorError(e) from e
        except CurlClientError as e:
            raise ValidatorError(e) from e
        except SourceError as e:
            raise ValidatorError(e) from e

    def validator_service(self) -> str:
        """
        Return the validator service url.
        """
        return self._base_url

    def get_validator_services(self) -> Dict:
        """
            Return the available domain validation types
        """
        return self._validation_types

    def get_domains(self) -> List:
        """
        The validator validation domains
        Returns:
            All available domains.
        """
        return list(self._validation_types.keys())

    def get_validation_types(self) -> List:
        """
        The validator validation domains
        Returns:
            All available domains.
        """
        return list(itertools.chain.from_iterable(self._validation_types.values()))


class ValidatorError(ValueError):
    """Validator errors."""
