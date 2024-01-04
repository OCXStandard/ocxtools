#  Copyright (c) 2023-2024. OCX Consortium https://3docx.org. See the LICENSE
"""OCX reporter module"""

# System imports
from collections import defaultdict
from typing import Dict, List, Union
# project imports

from ocxtools.parser.parser import OcxNotifyParser
from ocxtools.interfaces.interfaces import ABC, IObserver, ObservableEvent


def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten a nested dictionary.

    Parameters:
    - d: The input dictionary to be flattened.
    - parent_key: The parent key used for recursive calls.
    - sep: The separator used to concatenate keys.

    Returns:
    - A flattened dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif not isinstance(v, list):
            items.append((new_key, v))
    return dict(items)


class OcxReporter(IObserver, ABC):
    """OCX reporter observer class"""

    def __init__(self, observable: OcxNotifyParser):
        observable.subscribe(self)
        self._ocx_objects = defaultdict(list)

    def update(self, event: ObservableEvent, payload: Dict):
        self._ocx_objects[payload.get('name')].append(payload.get('object'))

    def element_count(self, selection: Union[List, str] = "All") -> List:
        """
        Return the count of a list of OCX elements in a model.

        Args:
            selection: Only count elements in the selection list. An empty list will count all elements.
        """
        if "All" in selection:
            return [{'Name': key, 'Count':
                    len(self._ocx_objects[key])} for key in sorted(self._ocx_objects)]
        else:
            return [{'Name': key, 'Count':
                    len(self._ocx_objects[key])} for key in sorted(self._ocx_objects) if key in selection]
