#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Converter client module. Implements the combination of the command and observer design patterns abstracting the
client from the conversion rules. """
# System imports
from abc import ABC
from enum import Enum
from typing import Dict, List

import packaging.version
# Third party imports
from loguru import logger

from ocxtools.exceptions import ConverterError, ConverterWarning
from ocxtools.interfaces.interfaces import IObservable, IObserver, IRule
# Project imports
from ocxtools.loader.loader import (DeclarationOfOcxImport, DynamicLoader,
                                    DynamicLoaderError)
from ocxtools.utils.utilities import all_equal


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


class DefaultRule(IRule):
    """The default rule."""

    def __init__(self):
        supported_version = DeclarationOfOcxImport("ocx", "3.0.0b4")
        super().__init__(supported_version)

    def convert(self, source_params: Dict, target: DeclarationOfOcxImport) -> Dict:
        """Default is no conversion."""
        return source_params

    def rule(self) -> RuleType:
        """Return the default rule type."""
        return RuleType.PASS  # Default


class Point3DRule(DefaultRule, ABC):
    """Mapping rule between source ``Point3D`` and target ``Point3D`` types."""

    def __init__(self):
        super().__init__()

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


class RefTypeRule(DefaultRule, IObserver, ABC):
    """Conversion rule for all reference types."""

    def __init__(self):
        supported_version = DeclarationOfOcxImport("ocx", "3.0.0b4")
        super().__init__(supported_version)

    def rule(self) -> RuleType:
        return RuleType.PARENT

    def convert(self, params: Dict, target: DeclarationOfOcxImport) -> Dict:
        try:
            source = params.get("ref_type").name
            target = DynamicLoader.import_class(target, "RefTypeValue")
            target_instance = getattr(target, source)
            params["ref_type"] = target_instance
            return params
        except DynamicLoaderError as e:
            logger.warning(e)
            return params


class CoordinateSystemRule(DefaultRule):
    """Conversion rule for the ``CoordinateSystem`` type."""

    def __init__(self):
        DeclarationOfOcxImport("ocx", "3.0.0b4")
        super().__init__()
        self._refplane = {}

    def rule(self) -> RuleType:
        return RuleType.COMPOSEDOF

    def listen_to_events(self) -> List:
        """The coordinate system event triggers"""
        return ["XrefPlanes", "YrefPlanes", "ZrefPlanes"]

    def update(self, event: str, params: Dict):
        """Update event"""
        self._refplane[event] = params
        logger.debug(f"CoordinateSystem event. Trigger: {event}, Message: {params}")

    def convert(self, params: Dict, target: DeclarationOfOcxImport) -> Dict:
        xrefplanes = f'Xrefplanes({self._refplane["XrefPlanes"]})'
        yrefplanes = f'Yrefplanes({self._refplane["YrefPlanes"]})'
        zrefplanes = f'Zrefplanes({self._refplane["ZrefPlanes"]})'
        return {
            "xref_planes": xrefplanes,
            "yref_planes": yrefplanes,
            "zref_planes": zrefplanes,
            "local_cartesian": params.get("local_cartesian"),
            "guidref": params.get("guidref"),
            "id": params.get("id"),
            "is_global": params.get("is_global"),
        }


class OcxConverter(IObservable, ABC):
    """
    Conversion class between different OCX model versions.

    Args:
        target: Declaration of the target model.

    Parameters:
        self._target: Declaration of the model version
        self._conversion_rule:
    """

    def __init__(self, target: DeclarationOfOcxImport):
        self._target = target
        self._conversion_rule = {}
        # My subscribers
        self._subsrcibers = set()
        # Store dynamically imported classes in a cash to prevent re-importing
        self._cashed = {}
        # Events tht will trigger message updates
        self._events = []
        # Register the available rules
        rules = [
            ("Origin", Point3DRule()),
            ("StartPoint", Point3DRule()),
            ("IntermediatePoint", Point3DRule()),
            ("EndPoint", Point3DRule()),
            ("Point3D", Point3DRule()),
            ("CenterOfGravity", Point3DRule()),
            ("Position", Point3DRule()),
            ("Occurrence", RefTypeRule()),
            ("RootRef", RefTypeRule()),
            ("ChildRef", RefTypeRule()),
            ("OcxItemPtr", RefTypeRule()),
            ("EdgeCurveRef", RefTypeRule()),
            ("SectionRef", RefTypeRule()),
            ("MaterialRef", RefTypeRule()),
            ("CoordinateSystem", CoordinateSystemRule()),
        ]
        for item in rules:
            self.register_rule(*item)

    def convert(self, name: str, source_params: Dict) -> Dict:
        """Convert the named object with source parameters"""

    def subscribe(self, observer: IRule):
        """Add a subscriber"""

        self._subsrcibers.add(observer)

    def unsubscribe(self, observer: IRule):
        """Remove a subscriber"""
        self._subsrcibers.remove(observer)

    def update(self, event: str, message: Dict):
        """Update subscribers"""
        if event in self._events:
            for subscriber in self._subsrcibers:
                subscriber.update(event, message)

    def register_event(self, events: List):
        """Register rule events."""
        for event in events:
            self._events.append(event)

    def register_rule(self, object_name: str, rule: IRule):
        """Register an object and a conversion rule."""
        self._conversion_rule[object_name] = rule
        self.subscribe(rule)
        self.register_event(rule.listen_to_events())

    def get_rule(self, name: str) -> IRule:
        """
        Obtain the conversion rule object.
        Args:
            name: The name of the source object.

        Returns:
            Conversion rule.
        """
        if name in self._conversion_rule:
            return self._conversion_rule.get(name)
        else:
            return DefaultRule()

    def class_factory(self, clazz, params):
        """Custom class factory method"""
        name = clazz.__name__
        self.update(name, params)
        logger.debug(f"Name: {name}, params: {params}")
        if name not in self._cashed:
            try:
                self._cashed[name] = DynamicLoader.import_class(self._target, name)
            except DynamicLoaderError:
                return None
        rule = self.get_rule(name)
        logger.debug(f"Conversion rule: {rule.rule()}")
        return self._cashed[name](**rule.convert(params, self._target))
