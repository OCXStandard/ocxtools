#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
# System imports
import json

import lxml.etree
from ocx_schema_parser.xelement import LxmlElement

from ocxtools import config
# Project imports
from ocxtools.validator.validator_client import (EmbeddingMethod,
                                                 OcxValidatorClient,
                                                 ValidationDomain,
                                                 ValidatorError)
from tests.conftest import AVEVA, SCHEMA_VERSION

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
    model = str(shared_datadir / AVEVA)
    response, header = client.validate_one(
        ocx_model=model, domain=ValidationDomain.OCX, embedding_method=EmbeddingMethod.BASE64
    )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'SUCCESS'



def test_validate_one_model_status_force_version_succeed(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / AVEVA)
    response, header = client.validate_one(
        ocx_model=model, domain=ValidationDomain.OCX, schema_version=SCHEMA_VERSION,
        embedding_method=EmbeddingMethod.STRING,
        force_version=True
    )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'SUCCESS'


def test_validate_one_model_status_force_version_fail(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / AVEVA)
    try:
        client.validate_one(
            ocx_model=model, domain=ValidationDomain.OCX, schema_version=SCHEMA_VERSION,
            embedding_method=EmbeddingMethod.STRING,
            force_version=True
        )
    except ValidatorError as e:
        assert 'invalid' in f'{e}'


def test_validate_one_model_status_code_500(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / AVEVA)
    response, header = client.validate_one(
        ocx_model=model, domain=ValidationDomain.OCX, embedding_method=EmbeddingMethod.BASE64
    )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'SUCCESS'


def test_validate_one_embedding_url(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / AVEVA)
    try:
        client.validate_one(model, ValidationDomain.OCX, embedding_method=EmbeddingMethod.URL)
    except ValidatorError as e:
        assert f"{e}" == "Embedding method 'URL' is not supported."



def test_validate_many(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    models = [str(shared_datadir / AVEVA), str(shared_datadir / AVEVA), str(shared_datadir / AVEVA)]
    response, headers = client.validate_many(
        ocx_models=models, domain=ValidationDomain.OCX, embedding_method=EmbeddingMethod.STRING
    )
    result = json.loads(response)
    # decoded_bytes = base64.b64decode(result[0].get('report'))
    assert 'report' in result[0].keys()
