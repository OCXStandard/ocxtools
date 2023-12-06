#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from pathlib import Path
from ocxtools.validator.validator_client import OcxValidatorCurlClient
from ocxtools.renderer.renderer import XsltTransformer
from ocxtools.validator.validator_report import ValidatorReport

from ocxtools import REPORT_FOLDER
class TestXsltRenderer:
    def test_render(self, shared_datadir):
        model = shared_datadir / 'm1_pp.3Docx'
        xslt_file = shared_datadir / 'resource' / 'gitb_trl_stylesheet_v1.0.xsl'
        transformer = XsltTransformer(str(xslt_file.resolve()))
        validator = OcxValidatorCurlClient(base_url='http://localhost:8080')
        response = validator.validate_one(str(model.resolve()), domain='ocx')
        report_data = ValidatorReport.create_report(model, response)
        report = report_data.report
        output_file = Path(transformer.render(data=report, source_file=str(model), output_folder= shared_datadir))
        assert output_file.exists()
        print(output_file.read_text())
