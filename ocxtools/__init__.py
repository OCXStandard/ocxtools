#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from pathlib import Path
from ocx_schema_parser.utils import utilities

__version__ = "0.1.0"
__app_name__ = "ocxtools"


# Secrets
# package configs
config_file = Path(__file__).parent / "config.yaml"  # The  config yaml
app_config = utilities.load_yaml_config(config_file)  # safe yaml load
WIKI_URL = app_config.get("WIKI_URL")
TEST_WIKI_URL = app_config.get("TEST_WIKI_URL")
DEFAULT_NSP = app_config.get("DEFAULT_NSP")
WORKING_DRAFT = app_config.get("WORKING_DRAFT")
SCHEMA_FOLDER = app_config.get("SCHEMA_FOLDER")
REPORT_FOLDER = app_config.get("REPORT_FOLDER")
VALIDATOR = app_config.get("VALIDATOR")
RESOURCES = app_config.get("RESOURCES")
XSLT_EN = app_config.get("XSLT_EN")

DOCKER_CONTAINER = app_config.get("DOCKER_CONTAINER")
DOCKER_IMAGE = app_config.get("DOCKER_IMAGE")
DOCKER_DESKTOP = app_config.get("DOCKER_DESKTOP")
