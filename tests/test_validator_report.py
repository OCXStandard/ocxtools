#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE


from ocxtools.validator.validator_client import EmbeddingMethod, OcxValidatorClient, ValidationDomain
from ocxtools.validator.validator_report import ValidatorReport
from ocxtools import VALIDATOR


def test_create_report(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1.3docx')
    response = client.validate_one(
        ocx_model=model, domain=ValidationDomain.OCX, embedding_method=EmbeddingMethod.BASE64
    )
    report = ValidatorReport.create_report(model, response)
    assert report.result == 'FAILURE'
