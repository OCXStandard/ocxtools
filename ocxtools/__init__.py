#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

__version__ = "0.1.0"
__app_name__ = "ocxtools"

from ocxtools.config import config

# Secrets
# package configs
# Validator
REPORT_FOLDER = config.get("ValidatorSettings", "report_folder")
VALIDATOR = config.get("ValidatorSettings", "validator_url")

# Docker
DOCKER_IMAGE = config.get("DockerSettings", "docker_image")
DOCKER_CONTAINER = config.get("DockerSettings", "container_name",)
DOCKER_TAG = config.get("DockerSettings", "docker_tag")
DOCKER_DESKTOP = config.get("DockerSettings", "docker_desktop")
DOCKER_PORT = int(config.get("DockerSettings", "docker_port"))
# Renderer
RESOURCES = config.get("RendererSettings", "resource_folder")
OCX_XSLT = config.get("RendererSettings", "ocx_xslt")
SCHEMATRON_XSLT = config.get("RendererSettings", "schematron_xslt")
# Serializer
JSON_INDENT = int(config.get("SerializerSettings", "json_indent"))
SERIALIZER_SUFFIX = config.get("SerializerSettings", "suffix")
# Defaults
README_FOLDER = config.get("Defaults", "readme_folder")
