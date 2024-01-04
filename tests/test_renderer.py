#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from pathlib import Path
from ocxtools.validator.validator_client import OcxValidatorClient, ValidationDomain
from ocxtools.renderer.renderer import XsltTransformer
from ocxtools.validator.validator_report import ValidatorReport

from ocxtools import config
RESOURCES = config.get("RendererSettings", "resource_folder")
OCX_XSLT = config.get("RendererSettings", "ocx_xslt")
SCHEMATRON_XSLT = config.get("RendererSettings", "schematron_xslt")
VALIDATOR = config.get('ValidatorSettings', 'validator_url')


class TestXsltRenderer:
    def test_ocx_html(self, shared_datadir):
        model = shared_datadir / 'm1.3docx'
        xslt_file = shared_datadir / RESOURCES / OCX_XSLT
        transformer = XsltTransformer(str(xslt_file.resolve()))
        validator = OcxValidatorClient(base_url=VALIDATOR)
        response = validator.validate_one(str(model.resolve()), domain=ValidationDomain.OCX)
        report_data = ValidatorReport.create_report(model, response)
        report = report_data.report
        output_file = Path(transformer.render(data=report, source_file=str(model), output_folder=shared_datadir))
        assert output_file.exists()
        print(output_file.name)

    def test_schematron_html(self, shared_datadir):
        model = shared_datadir / 'm1.3docx'
        xslt_file = shared_datadir / RESOURCES / SCHEMATRON_XSLT
        transformer = XsltTransformer(str(xslt_file.resolve()))
        validator = OcxValidatorClient(base_url=VALIDATOR)
        response = validator.validate_one(str(model.resolve()), domain=ValidationDomain.SCHEMATRON)
        report_data = ValidatorReport.create_report(model, response)
        report = report_data.report
        output_file = Path(transformer.render(data=report, source_file=str(model), output_folder=shared_datadir))
        assert output_file.exists()
        print(output_file.name)
