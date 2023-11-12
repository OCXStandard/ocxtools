#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Conversion module for converting OCX models from one version to another version"""
# System imports
from abc import ABC, abstractmethod
from abc import abstractproperty, abstractmethod, abstractstaticmethod
from typing import Dict

# Third party imports
from loguru import logger
import packaging.version

import ocxtools.ocx_converter

# Project imports
from ocxtools.loader import DynamicLoader, DeclarationOfOcxImport


class Mapper(ABC):
    """Abstract mapper interface"""

    def __init__(self, target: DeclarationOfOcxImport):
        self._target = target

    @abstractmethod
    def params(self, source_params: Dict) -> Dict:
        """Abstract Method: Return the mapped parameters."""
        return source_params
    @abstractmethod
    def replace(self, source: Dict, collection: Dict) -> Dict:
        pass
    def get_target_version(self) -> str:
        """Returns the target version."""
        return self._target.get_version()


class Point3DMapper(Mapper, ABC):
    """Mapping between source ``Point3D`` and target ``Point3D`` types."""

    def __init__(self, target: DeclarationOfOcxImport):
        super().__init__(target)

    def params(self, source: Dict) -> Dict:
        """Return the target object parameters."""
        if packaging.version.parse(self.get_target_version()).major < 3:
            return source
        coordinates = []
        unit = ''
        for k, v in source.items():
            coordinates.append(v.numericvalue)
            unit = v.unit
        return {'cooordinates': coordinates, 'unit': unit}


class CoordinateSystem(Mapper, ABC):
    def __init__(self, target: DeclarationOfOcxImport):
        super().__init__(target)

    def replace(self, source: Dict, prototype: Dict) -> Dict:
        pass


class OcxConverter:
    def __init__(self, target: DeclarationOfOcxImport):
        """
        Conversion class between different OCX model versions.

        Args:
            declaration: Declaration of the target model version

        Parameters:
            _mapper: Table of mapping objects
        """
        self._target = target
        # Store dynamically imported classes to prevent re-importing
        self._classes = {}
        # Mapping of objects requiring parameter transforms
        self._map = {'Origin': 'Point3DMapper'}
        self._not_implemented = ['VesselGrid']
        # Collect objects that cannot be directly mapped
        self._collect = ['FrameTables']
        self._collection = {}

    def collect(self, name):
        """Whether to collect an object or not."""
        if name in self._collect:
            return True
        return False

    def class_factory(self, clazz, params):
        """Custom class factory method"""
        name = clazz.__name__
        if name in self._not_implemented:
            return None
        logger.debug(f'{name}: {params}')
        if name not in self._classes:
            self._classes[name] = DynamicLoader.load_class(self._target, name)
        if name in self._map:
            mapper = getattr(ocxtools.converter, self._map[name])(self._target)
            obj = self._classes[name](**mapper.params(params))
            return obj
        if self.collect(name):
            self._collection[name] = self._classes[name](**params)
        return self._classes[name](**params)
