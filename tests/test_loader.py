#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.loader.loader import DeclarationOfOcxImport, DynamicLoader
from ocxtools.parser.parser import MetaData


def test_import_module():
    declaration = DeclarationOfOcxImport("ocx", "2.8.6")
    assert DynamicLoader.import_module(declaration)


def test_import_class():
    declaration = DeclarationOfOcxImport("ocx", "300b3")
    assert DynamicLoader.import_class(declaration, "Vessel")


def test_ref_type_name():
    class_name = "RefTypeValue"
    value = "OCX_VESSEL"
    declaration = DeclarationOfOcxImport("ocx", "300b3")
    data_class = DynamicLoader.import_class(declaration, class_name)
    instance = getattr(data_class, value)
    assert instance.name == "OCX_VESSEL"


def test_data_class_instance_namespace():
    class_name = "Vessel"
    declaration = DeclarationOfOcxImport("ocx", "300b3")
    data_class = DynamicLoader.import_class(declaration, class_name)()
    namespace = MetaData.namespace(data_class)
    assert (
        namespace == "https://3docx.org/fileadmin//ocx_schema//V300b3//OCX_Schema.xsd"
    )
