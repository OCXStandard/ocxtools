#  Copyright (c) 2024. OCX Consortium https://3docx.org. See the LICENSE
"""3Docx data classes"""
# System imports
from dataclasses import dataclass, field
from typing import List
from ocxtools.dataclass.dataclasses import BaseDataClass


@dataclass
class Plate(BaseDataClass):
    id:str = field(metadata={"header": "Id"})
    description:str = field(metadata={"header": "Id"})
    name:str = field(metadata={"header": "Id"})
    guidref:str = field(metadata={"header": "Id"})
    dry_weigth:float = field(metadata={"header": "Id"}, default=0)
    center_of_gravity: List = field(metadata={"header": "Id"}, default=list)
    external_geometry_ref:str = field(metadata={"header": "Id"}, default='')
    plate_material:str = field(metadata={"header": "Material"}, default='')
    plate_thickness:float = field(metadata={"header": "Id"}, default=0)
    offset: float = field(metadata={"header": "Id"}, default=0)
    function_type:str = field(metadata={"header": "Function Type"}, default=list)
