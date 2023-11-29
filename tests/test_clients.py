#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

import time
import lxml.etree
import base64
import json
from ocxtools.clients.clients import CurlRestClient, RequestType, RestClient
from ocxtools.validator.validator_client import EmbeddingMethod
from ocx_schema_parser.xelement import LxmlElement


class TestCurlClient:
    # def test_mock_get_data(self, mocker, clients) -> None:
    #     mocked_get_data_value = \
    #         [{"domain": "extensions",
    #           "validationTypes": [{"type": "rudder_v1.2.0", "description": "rudder_v1.2.0"}]},
    #          {"domain": "ocx",
    #           "validationTypes": [{"type": "ocx.v2.8.6", "description": "OCX XSD validation - v2.8.6"},
    #                               {"type": "ocx.v3.0.0b3", "description": "OCX XSD validation - v3.0.0b3"},
    #                               {"type": "ocx.v3.0.0b4", "description": "OCX XSD validation - v3.0.0b4"}]}]
    #
    #     mocker.patch('ocxtools.clients.clients.get_data',
    #                  return_value=mocked_get_data_value)
    #
    #     actual_mock_response = clients.get_data()

    def test_get_data(self):
        client = CurlRestClient("http://localhost:8080")
        response = client.api(RequestType.GET, endpoint="rest/api/info")
        result =  json.loads(response)
        domains = [item.get('domain') for item in result]
        assert 'ocx' in domains

    def test_post_data_string_embedding(self, shared_datadir):
        client = CurlRestClient("http://localhost:8080")
        model = shared_datadir / "m1_pp.3Docx"
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        content = byte_string.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.STRING.value,
            "validationType": "ocx.v3.0.0b3",
            "locationAsPath": False,
            "addInputToReport": False,
            "wrapReportDataInCDATA": False,
            "locale": "en",
        }
        client.set_headers(
            ["accept: application/json", "Content-Type: application/json"]
        )
        response = client.api(
            RequestType.POST, endpoint="rest/ocx/api/validate", payload=payload
        )
        assert json.loads(response).get('result') == 'FAILURE'

    def test_post_data_base64_embedding(self, shared_datadir):
        client = CurlRestClient("http://localhost:8080")
        model = shared_datadir / "m1_pp.3Docx"
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        base64_bytes = base64.b64encode(byte_string)
        content = base64_bytes.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.BASE64.value,
            "validationType": "ocx.v3.0.0b3",
            "locationAsPath": False,
            "addInputToReport": False,
            "wrapReportDataInCDATA": False,
            "locale": "en",
        }
        client.set_headers(
            ["accept: application/json", "Content-Type: application/json"]
        )
        response = client.api(
            RequestType.POST, endpoint="rest/ocx/api/validate", payload=payload
        )
        assert json.loads(response).get('result') == 'FAILURE'

    def test_post_data_xml_string_embedding(self, shared_datadir):
        tic = time.perf_counter()
        client = CurlRestClient("http://localhost:8080")
        model = shared_datadir / "m1_pp.3Docx"
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        content = byte_string.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.STRING.value,
            "validationType": "ocx.v3.0.0b3",
            "locationAsPath": False,
            "addInputToReport": True,
            "wrapReportDataInCDATA": False,
            "locale": "en",
        }
        client.set_headers(
            ["accept: application/xml", "Content-Type: application/json"]
        )
        response = client.api(
            RequestType.POST, endpoint="rest/ocx/api/validate", payload=payload
        )
        root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
        result = LxmlElement.find_child_with_name(root,'result')
        toc = time.perf_counter()
        assert result.text == 'FAILURE'
        print(f'Elapsed time: {toc-tic:04f} seconds')


class TestRestClient:
    def test_get_data(self):
        client = RestClient("http://localhost:8080")
        response = client.api(RequestType.GET, endpoint="rest/api/info")
        result =  json.loads(response)
        domains = [item.get('domain') for item in result]
        assert 'ocx' in domains

    def test_post_data_xml_string_embedding(self, shared_datadir):
        tic = time.perf_counter()
        client = RestClient("http://localhost:8080")
        model = shared_datadir / "m1_pp.3Docx"
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        content = byte_string.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.STRING.value,
            "validationType": "ocx.v3.0.0b3",
            "locationAsPath": False,
            "addInputToReport": True,
            "wrapReportDataInCDATA": False,
            "locale": "en",
        }
        client.set_headers(
            {"accept": "application/xml", "Content-Type": "application/json"}
        )
        response = client.api(
            RequestType.POST, endpoint="rest/ocx/api/validate", payload=payload
        )
        root = lxml.etree.fromstring(response.encode(encoding='utf-8'))
        result = LxmlElement.find_child_with_name(root,'result')
        toc = time.perf_counter()
        assert result.text == 'FAILURE'
        print(f'Elapsed time: {toc-tic:04f} seconds')

    def test_post_data_json_string_embedding(self, shared_datadir):
        client = RestClient("http://localhost:8080")
        model = shared_datadir / "m1_pp.3Docx"
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        content = byte_string.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.STRING.value,
            "validationType": "ocx.v3.0.0b3",
            "locationAsPath": False,
            "addInputToReport": True,
            "wrapReportDataInCDATA": False,
            "locale": "en",
        }
        client.set_headers(
            {"accept": "application/json", "Content-Type": "application/json"}
        )
        response = client.api(
            RequestType.POST, endpoint="rest/ocx/api/validate", payload=payload
        )
        assert json.loads(response).get('result') == 'FAILURE'

    def test_post_data_base64_embedding(self, shared_datadir):
        client = RestClient("http://localhost:8080")
        model = shared_datadir / "box.3Docx"
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        base64_bytes = base64.b64encode(byte_string)
        content = base64_bytes.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.BASE64.value,
            "validationType": "ocx.v2.8.6",
            "locationAsPath": False,
            "addInputToReport": True,
            "wrapReportDataInCDATA": False,
            "locale": "en",
        }
        client.set_headers(
            {"accept": "application/json", "Content-Type": "application/json"}
        )
        response = client.api(
            RequestType.POST, endpoint="rest/ocx/api/validate", payload=payload
        )
        assert json.loads(response).get('result') == 'FAILURE'
