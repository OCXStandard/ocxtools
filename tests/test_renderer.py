#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from pathlib import Path
from ocxtools.validator.validator_client import OcxValidatorClient
from ocxtools.renderer.renderer import XsltTransformer


class TestXsltRenderer:
    def test_render(self, shared_datadir):
        model = shared_datadir / 'm1_pp.3Docx'
        xslt_file = shared_datadir / 'resource' / 'gitb_trl_stylesheet_v1.0.xsl'
        transformer = XsltTransformer(str(xslt_file.resolve()))
        validator = OcxValidatorClient(base_url='http://localhost:8080')
        response = validator.validate_one(str(model.resolve()), domain='ocx')
        context = response.get('context')
        report =  context.get('items')[0].get('value')
        report_file = shared_datadir  / 'report.xml'
        with open(str(report_file.resolve()), 'w') as fp:
            fp.write(report)
        transformed_file = f'report_{model.stem}.html'
        transformer.render(str(report_file.resolve()),str(xslt_file.resolve()), transformed_file)
