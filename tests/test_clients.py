#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

import base64
import json
import time

import lxml.etree
from ocx_schema_parser.xelement import LxmlElement

from ocxtools.clients.clients import CurlRestClient, RequestType, RestClient
from ocxtools.validator.validator_client import EmbeddingMethod
from tests.conftest import AVEVA, SCHEMA_VERSION

VALIDATOR = "http://localhost:8080"


class TestCurlClient:

    def test_curl_get_data(self):
        client = CurlRestClient(VALIDATOR)
        response = client.api(RequestType.GET, endpoint="rest/api/info")
        result = json.loads(response)
        domains = [item.get('domain') for item in result]
        assert 'ocx' in domains

    def test_curl_post_data_string_embedding(self, shared_datadir):
        client = CurlRestClient(VALIDATOR)
        model = shared_datadir / AVEVA
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        content = byte_string.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.STRING.value,
            "validationType": f'ocx.v{SCHEMA_VERSION}',
            "locationAsPath": False,
            "addInputToReport": False,
            "wrapReportDataInCDATA": False,
            "locale": "en",
        }
        client.set_headers(
            {"accept": "application/json", "Content-Type": "application/json"}
        )
        response = client.api(
            RequestType.POST, endpoint="rest/ocx/api/validate", payload=payload
        )
        assert json.loads(response).get('result') == 'SUCCESS'

    def test_curl_post_data_base64_embedding(self, shared_datadir):
        client = CurlRestClient(VALIDATOR)
        model = shared_datadir / AVEVA
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        base64_bytes = base64.b64encode(byte_string)
        content = base64_bytes.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.BASE64.value,
            "validationType": f'ocx.v{SCHEMA_VERSION}',
            "locationAsPath": False,
            "addInputToReport": False,
            "wrapReportDataInCDATA": False,
            "locale": "en",
        }
        client.set_headers(
            {"accept": "application/json", "Content-Type": "application/json"}
        )
        response = client.api(
            RequestType.POST, endpoint="rest/ocx/api/validate", payload=payload
        )
        assert json.loads(response).get('result') == 'SUCCESS'

    def test_curl_post_data_xml_string_embedding(self, shared_datadir):
        tic = time.perf_counter()
        client = CurlRestClient(VALIDATOR)
        model = shared_datadir / AVEVA
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        content = byte_string.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.STRING.value,
            "validationType": f'ocx.v{SCHEMA_VERSION}',
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
        result = LxmlElement.find_child_with_name(root, 'result')
        toc = time.perf_counter()
        assert result.text == 'SUCCESS'
        print(f'Elapsed time: {toc - tic:04f} seconds')


class TestRestClient:
    def test_rest_get_data(self):
        client = RestClient(VALIDATOR)
        response = client.api(RequestType.GET, endpoint="rest/api/info")
        result = json.loads(response)
        domains = [item.get('domain') for item in result]
        assert 'ocx' in domains

    def test_rest_post_data_xml_string_embedding(self, shared_datadir):
        tic = time.perf_counter()
        client = RestClient(VALIDATOR)
        model = shared_datadir / AVEVA
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        content = byte_string.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.STRING.value,
            "validationType": f'ocx.v{SCHEMA_VERSION}',
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
        result = LxmlElement.find_child_with_name(root, 'result')
        toc = time.perf_counter()
        assert result.text == 'SUCCESS'
        print(f'Elapsed time: {toc - tic:04f} seconds')

    def test_rest_post_data_json_string_embedding(self, shared_datadir):
        client = RestClient(VALIDATOR)
        model = shared_datadir / AVEVA
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        content = byte_string.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.STRING.value,
            "validationType": f'ocx.v{SCHEMA_VERSION}',
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
        assert json.loads(response).get('result') == 'SUCCESS'

    def test_rest_post_data_base64_embedding(self, shared_datadir):
        client = RestClient(VALIDATOR)
        model = shared_datadir / AVEVA
        tree = lxml.etree.parse(str(model.resolve()))
        byte_string = lxml.etree.tostring(tree)
        base64_bytes = base64.b64encode(byte_string)
        content = base64_bytes.decode("utf-8")
        payload = {
            "contentToValidate": content,
            "embeddingMethod": EmbeddingMethod.BASE64.value,
            "validationType": f'ocx.v{SCHEMA_VERSION}',
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
        assert json.loads(response).get('result') == 'SUCCESS'
