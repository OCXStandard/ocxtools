#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from pathlib import Path
from ocxtools.validator.validator_client import OcxValidatorClient
from ocxtools.renderer.renderer import XsltTransformer
from ocxtools.validator.validator_report import ValidatorReport


class TestXsltRenderer:
    def test_render(self, shared_datadir):
        model = shared_datadir / 'm1_pp.3Docx'
        xslt_file = shared_datadir / 'resource' / 'gitb_trl_stylesheet_v1.0.xsl'
        transformer = XsltTransformer(str(xslt_file.resolve()))
        validator = OcxValidatorClient(base_url='http://localhost:8080')
        response = validator.validate_one(str(model.resolve()), domain='ocx')
        report_data = ValidatorReport.create_report(model, response)
        report = report_data.report.encode(encoding='utf-8')
        transformed_file = shared_datadir / f'report_{model.stem}.html'
        transformer.render(report, transformed_file.resolve())
        assert transformed_file.exists()
