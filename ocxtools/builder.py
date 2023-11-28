#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""The OCX model builder module."""

# system imports
import enum
from dataclasses import dataclass
from typing import Any, Dict

# 3rd party imports
from xsdata.models.datatype import (
    XmlBase64Binary,
    XmlDate,
    XmlDateTime,
    XmlDuration,
    XmlHexBinary,
    XmlPeriod,
    XmlTime,
)

# Project imports
from ocxtools.loader import DeclarationOfOcxImport, DynamicLoader
from ocxtools.parser import MetaData


def ocx_deepcopy(
    prototype_obj, declaration: DeclarationOfOcxImport, memo: Dict
) -> dataclass:
    """Recursively copy an OCX object"""
    name = MetaData.class_name(prototype_obj)
    clone = DynamicLoader.load_class(module_declaration=declaration, class_name=name)
    memo[id(prototype_obj)] = clone
    for k, v in prototype_obj.__dict__.items():
        setattr(clone, k, ocx_deepcopy(v, declaration, memo))
    return clone


def ocx_copy(prototype_obj, declaration: DeclarationOfOcxImport) -> dataclass:
    """Shallow copy of an OCX object"""
    name = MetaData.class_name(prototype_obj)
    clone = DynamicLoader.load_class(module_declaration=declaration, class_name=name)
    clone.__dict__.update(prototype_obj.__dict__)
    return clone


not_supported = ["VesselGrid", "FrameTables"]


def my_deepcopy(data, declaration: DeclarationOfOcxImport, memo) -> Any:
    result = data
    if isinstance(
        data,
        (
            int,
            float,
            type(None),
            str,
            bool,
            enum.Enum,
            XmlPeriod,
            XmlDate,
            XmlTime,
            XmlDateTime,
            XmlHexBinary,
            XmlBase64Binary,
            XmlDuration,
        ),
    ):
        result = data
    elif isinstance(data, dict):
        result = {
            key: my_deepcopy(value, declaration, memo) for key, value in data.items()
        }
        assert id(result) != id(data)
    elif isinstance(data, list):
        result = [my_deepcopy(item, declaration, memo) for item in data]
        assert id(result) != id(data)
    elif isinstance(data, tuple):
        aux = [my_deepcopy(item, declaration, memo) for item in data]
        result = tuple(aux)
        assert id(result) != id(data)
    elif hasattr(data, "__class__"):  # Its a dataclass
        name = MetaData.class_name(data)
        if name in not_supported:
            return result
        result = DynamicLoader.load_class(
            module_declaration=declaration, class_name=name
        )()
        if result is not None:
            memo[id(data)] = result
            for k, v in data.__dict__.items():
                setattr(result, k, my_deepcopy(v, declaration, memo))
            assert id(result) != id(data)
    else:
        raise ValueError("unexpected type")
    return result


class OcxModelBuilder:
    """The builder class."""

    def __init__(self, declaration: DeclarationOfOcxImport):
        self._declaration = declaration

    def build(self, prototype) -> dataclass:
        """Build the new dataclass hierarchy from the prototype dataclass."""
        memo = {}
        return my_deepcopy(prototype, self._declaration, memo)