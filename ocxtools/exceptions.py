#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module exceptions."""


class ConverterError(ValueError):
    """Converter related errors."""


class ConverterWarning(Warning):
    """Converter related warnings."""


class XmlParserError(ValueError):
    """Parser errors."""


class SourceError(ValueError):
    """SourceValidator errors."""


class ReporterError(ValueError):
    """Reporter errors."""
