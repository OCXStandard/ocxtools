#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

import json
import time
import lxml.etree


from ocxtools.exceptions import ValidatorError
from ocxtools.validator.validator_client import EmbeddingMethod, OcxValidatorClient
from ocx_schema_parser.xelement import LxmlElement

VALIDATOR = 'http://localhost:8080'


def test_get_validator_info():
    client = OcxValidatorClient(VALIDATOR)
    response = json.dumps(client.get_validator_info())
    assert 'domain' in response


def test_validate_one_model_status(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1_pp.3docx')
    response = client.validate_one(
                ocx_model=model, domain='ocx', embedding_method=EmbeddingMethod.STRING
            )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'FAILURE'

def test_validate_one_model_status_force_version(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm2_pp.3docx')
    response = client.validate_one(
                ocx_model=model, domain='ocx', schema_version='3.0.0b3',
                embedding_method=EmbeddingMethod.STRING,
                force_version= True
            )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'FAILURE'


def test_validate_one_model_status_code_500(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1_pp.3docx')
    response =  client.validate_one(
                ocx_model=model, domain='ocx', embedding_method=EmbeddingMethod.BASE64
            )
    root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
    result = LxmlElement.find_child_with_name(root, 'result')
    assert result.text == 'FAILURE'


def test_validate_one_embedding_url(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'box_pp.3docx')
    try:
        client.validate_one(model, 'ocx', embedding_method=EmbeddingMethod.URL)
    except ValidatorError as e:
        assert f"{e}" == "Embedding method 'URL' is not supported."
