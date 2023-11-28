#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module exceptions."""
import requests
from pycurl import error as pycurl_error


class ConverterError(ValueError):
    """Converter related errors."""


class ConverterWarning(Warning):
    """Converter related warnings."""


class DynamicLoaderError(AttributeError):
    """Dynamic import errors."""


class XmlParserError(ValueError):
    """Parser errors."""


class RenderError(ValueError):
    """Render errors."""


class ValidatorError(ValueError):
    """Validator errors."""


class SerializerError(ValueError):
    """OCX Serializing errors."""


class RequestClientError(requests.RequestException):
    """Request client errors."""


class CurlClientError(pycurl_error):
    """Curl client errors."""


class SourceError(ValueError):
    """SourceValidator errors."""
