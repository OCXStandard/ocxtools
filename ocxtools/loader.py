#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Dynamically load a python module."""

# system imports
import sys
from typing import Tuple, List, Any
import importlib
from types import ModuleType
from abc import ABC, abstractmethod
from abc import abstractproperty, abstractmethod, abstractstaticmethod

from dataclasses import fields, dataclass
# 3rd party imports
from loguru import logger


class IModuleDeclaration(ABC):
    """Abstract Method Interface"""

    @staticmethod
    @abstractmethod
    def get_declaration() -> str:
        """Abstract Method: Return the module declaration string."""
        pass


class DeclarationOfOcxImport(IModuleDeclaration):
    """Declaration of the ocx module."""

    def __init__(self, name: str, version: str):
        self._name = name
        self._version = version

    def get_declaration(self) -> str:
        """Return the module import declaration."""
        ocx_pkg = f'{self._name}_{self._version.replace(".", "")}'
        return f'{self._name}.{ocx_pkg}.{ocx_pkg}'

    def get_version(self) -> str:
        """Return the OCX module version."""
        return self._version

    def get_name(self) -> str:
        """Return the declared module name."""
        return self._name

class DynamicLoader():
    """Dynamically loads modules, classes of functions from a module declaration."""

    @classmethod
    def _load(cls, declaration: str) -> Any:
        """Internal Method: Import the object from the declaration.

        Args:
            declaration: The module declaration string.
        Returns:
            Return the loaded object, None if failed.
        """
        obj_type = None
        if (spec := importlib.util.find_spec(declaration)) is not None:
            obj_type = importlib.util.module_from_spec(spec)
            sys.modules[declaration] = obj_type
            spec.loader.exec_module(obj_type)
            # logger.debug(f"Loaded object {declaration!r} from location {spec.origin!r}")
        else:
            logger.error(f'No object {declaration!r}')
        return obj_type

    @classmethod
    def load_module(cls, module_declaration: IModuleDeclaration) -> ModuleType:
        """

        Args:
            module_declaration: The declaration of the pyton module to load

        Returns:
            Return the loaded module, None if failed.
        """
        module_to_load = module_declaration.get_declaration()
        return cls._load(module_to_load)

    @classmethod
    def load_class(cls, module_declaration: IModuleDeclaration, class_name: str) -> Any:
        """

        Args:
            class_name: The class name to load form the declared module
            module_declaration: The declaration of the pyton module to load

        Returns:
            Return the loaded class, None if failed.
        """
        obj = None
        module_to_load = module_declaration.get_declaration()
        module = cls._load(module_to_load)
        try:
            obj = getattr(module, class_name)
            # logger.debug(f"Loaded class {class_name!r}")
        except AttributeError as e:
            logger.error(f'No class with name {class_name!r} in module {module_to_load!r}')
        return obj
    @classmethod
    def get_all_class_names(cls, module_name: str, version: str) -> List:
        """Return all class names in the module by the ``__all__`` variable.

        Args:
            module_name: The module name
            version: The module version

        Returns:
            The list of available module class names.
        """
        all_names = []
        ocx_pkg = f'{module_name}_{version.replace(".", "")}'
        ocx_module = f'{module_name}.{ocx_pkg}'
        if (spec := importlib.util.find_spec(ocx_module)) is not None:
            module = importlib.util.module_from_spec(spec)
            sys.modules[ocx_module] = module
            spec.loader.exec_module(module)
            logger.debug(f"Found module {ocx_module!r} in location {spec.origin}")
            all_names = module.__all__
        else:
            logger.error(f'No module with name {module_name!r} and version {version!r}')
        return all_names
