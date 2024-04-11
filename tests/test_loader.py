#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocxtools.loader.loader import DeclarationOfOcxImport, DynamicLoader
from ocxtools.parser.parser import MetaData
from tests.conftest import SCHEMA_VERSION


def test_import_module():
    declaration = DeclarationOfOcxImport("ocx", "2.8.6")
    assert DynamicLoader.import_module(declaration)


def test_import_class():
    declaration = DeclarationOfOcxImport("ocx", SCHEMA_VERSION)
    assert DynamicLoader.import_class(declaration, "Vessel")


def test_ref_type_name():
    class_name = "RefTypeValue"
    value = "OCX_VESSEL"
    declaration = DeclarationOfOcxImport("ocx",  SCHEMA_VERSION)
    data_class = DynamicLoader.import_class(declaration, class_name)
    instance = getattr(data_class, value)
    assert instance.name == "OCX_VESSEL"


def test_data_class_instance_namespace():
    class_name = "Vessel"
    declaration = DeclarationOfOcxImport("ocx",  SCHEMA_VERSION)
    data_class = DynamicLoader.import_class(declaration, class_name)()
    namespace = MetaData.namespace(data_class)
    repo_folder = SCHEMA_VERSION.replace('.','')
    repo_folder = f'V{repo_folder}'
    assert (
        namespace == f'https://3docx.org/fileadmin//ocx_schema//{repo_folder}//OCX_Schema.xsd'
    )
