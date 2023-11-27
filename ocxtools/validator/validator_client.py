#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""OCX validator client module."""
import base64
import json
from enum import Enum

# System imports
from pathlib import Path

# 3rd party imports
import lxml.etree
from loguru import logger

# Project
from ocxtools.clients.clients import CurlRestClient, RequestType
from ocxtools.exceptions import CurlClientError, ValidatorError
from ocxtools.utils.utilities import OcxVersion, SourceValidator


class EmbeddingMethod(Enum):
    """Embedding type."""

    STRING = "STRING"
    URL = "URL"
    BASE64 = "BASE64"


class OcxValidatorClient(CurlRestClient):
    """OCX validator client"""

    def __init__(self, base_url):
        super().__init__(base_url)

    def get_validator_info(self) -> json:
        """Retrieve the OCX docker validator interface information."""
        endpoint = "rest/api/info"
        self.set_headers(["Accept: application/json"])
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
            add_input_to_report: If True, add the input source to the report. Default = ``False``
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
        endpoint = f"rest/{domain}/api/validate"
        params = {
            "contentToValidate": content,
            "embeddingMethod": embedding_method,
            "validationType": validation_type,
            "locationAsPath": location_as_path,
            "addInputToReport": add_input_to_report,
            "wrapReportDataInCDATA": wrap_report_data_in_cdata,
            "locale": locale,
        }
        self.set_headers(["accept: application/json", "Content-Type: application/json"])
        return self.api(
            request_type=RequestType.POST, endpoint=endpoint, payload=params
        )

    def validate_one(
        self,
        ocx_model: str,
        domain: str = "ocx",
        embedding_method: EmbeddingMethod = EmbeddingMethod.BASE64,
    ) -> json:
        """Validate a single 3Docx XML file. The XML file will be pretty-print formatted before validation.

        Args:
            embedding_method: The content embedding method.
            ocx_model: The model source path
            domain: The validator validation domain

        Returns:
            The validator response

        Raises:
            ValidatorError on a bad response.
        """
        try:
            Path(SourceValidator.validate(ocx_model))
            version = OcxVersion.get_version(ocx_model)
            # parser = OcxParser()
            # ocxxml = parser.parse(str(file_path))
            # serializer = Serializer(ocxxml)
            # decoded_str = serializer.serialize_xml()
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
                        f"Embedding method {embedding_method} is not supported."
                    )
            response = self._validate(
                content,
                domain,
                validation_type,
                embedding_method.value,
                location_as_path,
            )
            return response
        except lxml.etree.LxmlError as e:
            logger.error(e)
            raise ValidatorError(e) from e
        except CurlClientError as e:
            raise ValidatorError(e) from e

    def validator_service(self) -> str:
        """
        Return the validator service url.
        """
        return self._base_url
