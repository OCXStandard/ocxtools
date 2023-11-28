#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

import json
from ocxtools.validator.validator_client import EmbeddingMethod, OcxValidatorClient
from ocxtools.validator.validator_report import ValidatorReport

VALIDATOR = 'http://localhost:8080'

def test_create(shared_datadir):
    client = OcxValidatorClient(VALIDATOR)
    model = str(shared_datadir / 'm1_pp.3docx')
    response = json.loads(
        json.dumps(
            client.validate_one(
                ocx_model=model, domain='ocx', embedding_method=EmbeddingMethod.BASE64
            )
        )
    )
    reporter = ValidatorReport(model)
    report = reporter.create(response)
    print(report)
