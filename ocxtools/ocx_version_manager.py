#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""OCX databinding version management."""
# system imports
import sys
from pathlib import Path
from typing import Tuple, List, Any
import importlib
from types import ModuleType
from dataclasses import fields, dataclass
# 3rd party imports
from loguru import logger


class VersionManager:
    """
        OCX databinding version management and dynamic module loading.
    """

    def __init__(self):
        pass

    @staticmethod
    def ocx_class_factory(clazz, params):
        """Custom class factory for the OCX root element

        Args:
            clazz:
            params:

        Returns:

        """
        if clazz.__name__ == 'OcxXmlT':
            return clazz(**{k: v.upper() for k, v in params.items()})
        return clazz(**params)

    @staticmethod
    def ocx_version(ocx_model: Path) -> str:
        """Return the OCX schema version of the model.

        Args:
            ocx_model: The 3Docx model

        Returns:
              The OCX schema version of the model.
        """
        version = 'NA'
        content = ocx_model.read_text().split()
        for item in content:
            if 'schemaVersion' in item:
                version = item[item.find('=') + 2:-1]
        return version

    @staticmethod
    def ocx_namespace(ocx_model: Path) -> str:
        """Return the OCX schema namespace of the model.

        Args:
            ocx_model: The 3Docx model

        Returns:
              The OCX schema version of the model.
        """
        namespace = 'NA'
        content = ocx_model.read_text().split()
        for item in content:
            if 'xmlns:ocx' in item:
                namespace = item[item.find('=') + 2:-1]
        return namespace

    @staticmethod
    def dynamic_import(module_name: str, version: str) -> ModuleType:
        """Dynamically load a module.

        Args:
            module_name: The module name
            version: The module version

        Returns:
            The module if loaded, None if not.
        """
        module = None
        ocx_pkg = f'{module_name}_{version.replace(".", "")}'
        ocx_module = f'{module_name}.{ocx_pkg}.{ocx_pkg}'
        if (spec := importlib.util.find_spec(ocx_module)) is not None:
            module = importlib.util.module_from_spec(spec)
            sys.modules[ocx_module] = module
            spec.loader.exec_module(module)
            logger.debug(f"Found module {ocx_module!r} in location {spec.origin}")
        else:
            logger.error(f'No module {ocx_module!r}')
        return module

    @staticmethod
    def get_all_class_names(module_name: str, version: str) -> List:
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

    @staticmethod
    def dynamic_import_class(module_name: str, version: str, class_name: str) -> Any:
        """Return the dataclass from the module ``module_name``.

        Args:
            version: The module version
            module_name: The module name
            class_name: The dataclass to return

        Returns:
            The named dataclass.
        """
        module = VersionManager.dynamic_import(module_name, version)
        data_class = getattr(module, class_name)
        return data_class

    @staticmethod
    def compare_class_names(version_1: str, version_2: str) -> Tuple:
        """Compare dataclass names between two schema versions.

        Args:
            version_1: Schema version 1
            version_2: Schema version 2

        Returns:
            version_1 and version_2 unique class names
        """
        module = 'ocx'
        v1_class_names = set(VersionManager.get_all_class_names(module, version_1))
        v2_class_names = set(VersionManager.get_all_class_names(module, version_2))
        logger.debug(f'{version_1!r} names: {len(v1_class_names)}')
        logger.debug(f'{version_2!r} names: {len(v2_class_names)}')
        common = v1_class_names.intersection(v2_class_names)
        only_v1 = v1_class_names - common
        only_v2 = v2_class_names - common
        return only_v1, only_v2

    @staticmethod
    def get_dataclass_field_names(data_class) -> List:
        """Dataclass field_names.

        Args:
            data_class: the dataclass instance

        Returns:
            dataclass filed names
        """
        attributes = []
        for item in data_class.__dataclass_fields__:
            attributes.append(item)
        return attributes

    @staticmethod
    def get_dataclass_meta(data_class) -> List:
        """Dataclass meta data .

        Args:
            data_class: the dataclass instance

        Returns:
            The class metadata
        """
        meta = {}
        for key, value in data_class.Meta.__dict__.items():
            meta[key] = value
        return meta
