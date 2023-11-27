#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Factory module for creating python objects."""

# system imports
from dataclasses import dataclass

# Project imports
from ocxtools.loader import DeclarationOfOcxImport, DynamicLoader


class PrototypeProxy:
    """Creates a new OCX instance by cloning from an existing OCX instance."""

    def __init__(self, declaration: DeclarationOfOcxImport, class_name: str):
        self._clone = DynamicLoader.load_class(declaration, class_name)()

    def clone(self, prototype_instance) -> dataclass:
        """
        Clone from a prototype datclass instance.

        Args:
            target_class: Name of the clone
            prototype_instance: The prototype instance to be cloned.

        Returns:
            A deepcopy of the prototype instance.
        """
        for k, v in prototype_instance.__dict__.items():
            print(f"k: {k}, v: {type(v)}")
        return self._clone()
