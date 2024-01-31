#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE


from ocxtools.validator.validator_client import EmbeddingMethod, OcxValidatorClient, ValidationDomain
from ocxtools.validator.validator_report import ValidatorReportFactory
from ocxtools import config
VALIDATOR = config.get('ValidatorSettings', 'validator_url')


def test_create_report(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1.3docx')
    response, header = client.validate_one(
        ocx_model=model, domain=ValidationDomain.OCX, embedding_method=EmbeddingMethod.BASE64
    )
    report = ValidatorReportFactory.create_report(model, response, header)
    assert report.result == 'FAILURE'
