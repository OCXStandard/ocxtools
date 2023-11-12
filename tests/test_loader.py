#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.loader import DynamicLoader, DeclarationOfOcxImport


def test_load_module():
    declaration = DeclarationOfOcxImport('ocx', '2.8.6')
    assert DynamicLoader.load_module(declaration)


def test_load_class():
    declaration = DeclarationOfOcxImport('ocx', '300b3')
    assert DynamicLoader.load_class(declaration, 'FreeboardTypeValue')


def test_named_class_instance():
    class_name = 'FreeboardTypeValue'
    declaration = DeclarationOfOcxImport('ocx', '300b3')
    obj = DynamicLoader.load_class(declaration, class_name)('A')
    print(obj)
