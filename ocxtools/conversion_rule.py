#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Conversion rules for converting between different OCX model versions."""
# System imports
from abc import ABC, abstractmethod
from enum import Enum
from itertools import groupby
from typing import Dict

# Third party imports
import packaging.version
from loguru import logger

from ocxtools.exceptions import ConverterError, ConverterWarning

# Project imports
from ocxtools.loader.loader import DeclarationOfOcxImport


class RuleType(Enum):
    """
    Rule type enumeration.

    Parameters:
        PASS: No conversion needed (Default)
        PARENT: The target parent changed. Applies to all objects that has the same parent type.
        RENAMED: The source object was renamed, but otherwise unchanged.
        MOVED: The source object was moved to another object.
        OBSOLETE: The object is deleted and is obsolete.
        USEDBY: The source object is used by a target object.
        COMPOSEDOF: The target object depends on other objects.
    """

    PASS = "pass"
    PARENT = "parent"
    RENAMED = "renamed"
    MOVED = "moved"
    OBSOLETE = "obsolete"
    USEDBY = "usedby"
    COMPOSEDOF = "composed_of"


def all_equal(iterable) -> True:
    """
    Verify that all items in a list are equal
    Args:
        iterable:

    Returns:
        True if all are equal, False otherwise.
    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


class IObserver(ABC):
    """The observer interface"""

    @abstractmethod
    def update(self, message):
        """update method"""


class IRule(ABC):
    """Abstract rule interface"""

    def __init__(self, latest: DeclarationOfOcxImport):
        self._latest_version = latest

    @abstractmethod
    def convert(self, source_params: Dict, target: DeclarationOfOcxImport) -> Dict:
        """Abstract Method: Return the mapped parameters."""
        pass

    def rule(self) -> RuleType:
        """Return the rule type."""
        return RuleType.PASS  # Default

    def get_latest_version(self) -> str:
        """Returns the latest supported version."""
        return self._latest_version.get_version()

    def validate_version(self, target: DeclarationOfOcxImport) -> bool:
        """

        Args:
            target:

        Returns:
            True if the conversion is implemented for the target version.
        """
        target_version = packaging.version.parse(target.get_version())
        if target_version.__gt__(packaging.version.parse(self.get_latest_version())):
            raise ConverterError(
                f"Conversion to {target.get_version()!r} is not supported. "
                f"Supported versions <= {self.get_latest_version()!r}"
            )
        return True


class DefaultRule(IRule, IObserver, ABC):
    """The default rule."""

    def __init__(self):
        supported_version = DeclarationOfOcxImport("ocx", "3.0.0b4")
        super().__init__(supported_version)

    def convert(self, source_params: Dict, target: DeclarationOfOcxImport) -> Dict:
        """Default is no conversion."""
        return source_params


class Point3DRule(IRule, ABC):
    """Mapping rule between source ``Point3D`` and target ``Point3D`` types."""

    def __init__(self):
        supported_version = DeclarationOfOcxImport("ocx", "3.0.0b4")
        super().__init__(supported_version)

    def rule(self) -> RuleType:
        """The RuleType of the Point3D type."""
        return RuleType.PARENT

    def convert(self, source: Dict, target: DeclarationOfOcxImport) -> Dict:
        """Return the target object parameters."""
        self.validate_version(target)
        result = source
        target_version = packaging.version.parse(target.get_version())
        if target_version.__gt__(packaging.version.parse(self.get_latest_version())):
            raise ConverterError(
                f"Conversion to {target.get_version()!r} is not supported. "
                f"Supported versions <= {self.get_latest_version()!r}"
            )
        if target_version.__le__(packaging.version.parse("2.8.6")):
            return source
        coordinates = []
        units = []
        for k, v in source.items():
            coordinates.append(v.numericvalue)
            units.append(v.unit)
        if not all_equal(units):
            raise ConverterWarning("Ambiguous unit conversion of Point3D object")
        unit = units[0]
        if target_version.pre[1] == 3:
            result = {"cooordinates": coordinates, "unit": unit}
        elif target_version.pre[1] == 4:
            result = {"coordinates": coordinates, "unit": unit}
        logger.debug(
            f"Target version: {target_version.public}. Converted params: {result} "
        )
        return result


class CoordinateSystem(IRule, IObserver, ABC):
    """Conversion rule for the ``CoordinateSystem`` type."""

    def __init__(self):
        supported_version = DeclarationOfOcxImport("ocx", "3.0.0b4")
        super().__init__(supported_version)
        self.subscribe

    def rule(self) -> RuleType:
        return RuleType.COMPOSEDOF


class FrameTables(IRule, ABC):
    """Conversion rule for the ``FrameTables`` type."""

    def __init__(self):
        supported_version = DeclarationOfOcxImport("ocx", "3.0.0b4")
        super().__init__(supported_version)

    def rule(self) -> RuleType:
        return RuleType.USEDBY
