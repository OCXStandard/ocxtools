#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
from ocx.ocx_286.ocx_286 import X, Y, Z
from ocxtools.converter import Point3DMapper
from ocxtools.loader import DeclarationOfOcxImport
def test_point3d_params():
    params = {'x': X(numericvalue=1.0, unit='Um'), 'y': Y(numericvalue=2.0, unit='Um'),
              'z': Z(numericvalue=3.0, unit='Um')}
    target = DeclarationOfOcxImport('ocx', '3.0.0b3')
    map = Point3DMapper(target)
    result = map.params(params)
    assert result == {'cooordinates': [1.0, 2.0, 3.0], 'unit': 'Um'}