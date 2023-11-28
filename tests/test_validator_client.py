#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

import json

from ocxtools.exceptions import ValidatorError
from ocxtools.validator.validator_client import EmbeddingMethod, OcxValidatorClient

VALIDATOR = 'http://localhost:8080'


def test_get_validator_info():
    client = OcxValidatorClient(VALIDATOR)
    response = json.dumps(client.get_validator_info())
    assert 'domain' in response


def test_validate_one_model_status_code_200(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1_pp.3docx')
    response = json.loads(
        json.dumps(
            client.validate_one(
                ocx_model=model, domain='ocx', embedding_method=EmbeddingMethod.STRING
            )
        )
    )
    assert response.get('result') == 'FAILURE'


def test_validate_one_model_status_code_500(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'midship.3docx')
    response = json.loads(
        json.dumps(
            client.validate_one(
                ocx_model=model, domain='ocx', embedding_method=EmbeddingMethod.BASE64
            )
        )
    )
    assert response.get('result') == 'FAILURE'


def test_validate_one_embedding_url(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'box_pp.3docx')
    try:
        client.validate_one(model, 'ocx', embedding_method=EmbeddingMethod.URL)
    except ValidatorError as e:
        assert f"{e}" == "Embedding method 'URL' is not supported."
