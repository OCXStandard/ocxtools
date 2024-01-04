#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
# System imports
import json
import lxml.etree
# Project imports
from ocxtools.validator.validator_client import EmbeddingMethod, OcxValidatorClient, ValidatorError, ValidationDomain
from ocx_schema_parser.xelement import LxmlElement
from ocxtools import config
VALIDATOR = config.get('ValidatorSettings', 'validator_url')


def test_get_validator_info():
    client = OcxValidatorClient(VALIDATOR)
    response = json.dumps(client.get_validator_info())
    assert 'domain' in response


def test_get_validator_validation_types():
    client = OcxValidatorClient(VALIDATOR)
    services = client.get_validator_services()
    assert 'ocx' in services


def test_validate_one_model_status(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1.3docx')
    response = client.validate_one(
        ocx_model=model, domain=ValidationDomain.OCX, embedding_method=EmbeddingMethod.STRING
    )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'FAILURE'


def test_validate_one_model_status_force_version_succeed(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1.3docx')
    response = client.validate_one(
        ocx_model=model, domain=ValidationDomain.OCX, schema_version='3.0.0b3',
        embedding_method=EmbeddingMethod.STRING,
        force_version=True
    )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'FAILURE'


def test_validate_one_model_status_force_version_fail(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1.3docx')
    try:
        client.validate_one(
            ocx_model=model, domain=ValidationDomain.OCX, schema_version='0.0.0',
            embedding_method=EmbeddingMethod.STRING,
            force_version=True
        )
    except ValidatorError as e:
        assert 'invalid' in f'{e}'


def test_validate_one_model_status_code_500(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1.3docx')
    response = client.validate_one(
        ocx_model=model, domain=ValidationDomain.OCX, embedding_method=EmbeddingMethod.BASE64
    )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'FAILURE'


def test_validate_one_embedding_url(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1.3docx')
    try:
        client.validate_one(model, ValidationDomain.OCX, embedding_method=EmbeddingMethod.URL)
    except ValidatorError as e:
        assert f"{e}" == "Embedding method 'URL' is not supported."


def test_validate_many(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    models = [str(shared_datadir / 'm1.3docx'), str(shared_datadir / 'm2.3docx'), str(shared_datadir / 'm3.3docx')]
    response = client.validate_many(
        ocx_models=models, domain=ValidationDomain.OCX, embedding_method=EmbeddingMethod.STRING
    )
    result = json.loads(response)
    # decoded_bytes = base64.b64decode(result[0].get('report'))
    assert 'report' in result[0].keys()
