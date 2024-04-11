#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Interfaces module."""

# System imports
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterator, List

import packaging.version

# Project imports
from ocxtools.exceptions import ConverterError


class ObservableEvent(Enum):
    """Events that can be listened to and broadcast."""
    DATACLASS = 'dataclass'
    REPORT = 'report'
    SERIALIZE = 'serialize'


class IModuleDeclaration(ABC):
    """Abstract module import declaration Interface"""

    @staticmethod
    @abstractmethod
    def get_declaration() -> str:
        """Abstract Method: Return the module declaration string."""
        pass


class IObserver(ABC):
    """The observer interface"""

    @abstractmethod
    def update(self, event: ObservableEvent, payload: Dict):
        """Interface update method"""


class IObservable(ABC):
    """Interface. The observable object."""

    @abstractmethod
    def subscribe(self, observer: IObserver):
        """subscription"""

    @abstractmethod
    def unsubscribe(self, observer: IObserver):
        """unsubscribe"""

    @abstractmethod
    def update(self, event: ObservableEvent, message: Dict):
        """
        update method.
        Args:
            event: The event type
            message: The event message
        """


class IRule(IObserver, ABC):
    """Abstract rule interface"""

    def __init__(self, latest: IModuleDeclaration):
        self._latest_version = latest

    @abstractmethod
    def convert(self, source_params: Dict, target: IModuleDeclaration) -> Dict:
        """Abstract Method: Return the mapped parameters."""
        pass

    def get_latest_version(self) -> str:
        """Returns the latest supported version."""
        return self._latest_version.get_version()

    def validate_version(self, target: IModuleDeclaration) -> bool:
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

    def update(self, event: str, message: Dict):
        """Default update is to do nothing"""
        pass

    def listen_to_events(self) -> List:
        """Default is to subscribe to no events"""
        return []


class IParser(ABC):
    """Abstract IParser interface."""

    @abstractmethod
    def parse(self, model: str) -> dataclass:
        """
        Abstract method for parsing a data model,

        Args:
            model: the data model source

        Returns:
            the root dataclass of the parsed data model.
        """
        pass

    @abstractmethod
    def iterator(self, model) -> Iterator:
        """
        Abstract method for iterating a data model.

        Args:
            model: the data model to iterate on.
        Returns:
             An iterator
        """
        pass


class ISerializer(ABC):
    """OcxSerializer interface"""

    def __init__(self, model: dataclass):
        self.model = model

    @abstractmethod
    def serialize_to_file(self, to_file: str) -> bool:
        """Abstract XML serialize to file method"""
        pass

    @abstractmethod
    def serialize_to_string(self) -> str:
        """Abstract XML serialize to string method"""
        pass
