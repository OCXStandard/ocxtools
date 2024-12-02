#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""App configuration"""

import configparser

# Project imports
from ocxtools import __app_name__

# Create a ConfigParser object
config = configparser.ConfigParser()

# Add sections and options programmatically

config["Defaults"] = {
    "command_history": f"{__app_name__}.hist",
    "text_editor": "notepad",
    "debug": True,
    "readme_folder": "readme",
    "register_issue": "https://github.com/OCXStandard/ocxtools/issues"
}

config["WikiSettings"] = {
    "wiki_url": "https://ocxwiki.3docx.org/",
    "default_namespace": "ocx",
}

config["ValidatorSettings"] = {
    "validator_url": "http://localhost:8080",
    # The validator stores validation reports in this sub-folder
    "report_folder": "reports",
    # The file suffix for the reports
    "report_suffix": '_validation.xml',
}

config["DockerSettings"] = {
    "container_name": "validator",
    "docker_image": "3docx/validator",
    "docker_tag": "latest",
    "docker_desktop": "C:/Program Files/Docker/Docker/Docker Desktop.exe",
    "docker_port": 8080
}

config["JupyterSettings"] = {
    "container_name": "jupyter",
    "docker_image": "jupyter/scipy-notebook",
    "docker_tag": "latest",
    "jupyter_mount": "/home/jovyan/work",
    "docker_port": 8888,
    "mount_folder": './reports'
}

config["RendererSettings"] = {
    # XSLT Style sheet resource folder
    "resource_folder": "resources",
    "ocx_xslt": "gitb_trl_stylesheet_v1.0.xsl",
    #  "schematron_xslt": "schematron_stylesheet.xsl"
    "schematron_xslt": "gitb_trl_stylesheet_v1.0.xsl"
}

config["SerializerSettings"] = {
    "json_indent": 4,
    "suffix": "_serialized",
}

config["FileLogger"] = {
    'log_file': f'{__app_name__}.log',
    "level": 'INFO',
    "retention": "14 days",
    "rotation": "10 MB",
}

config["StdoutLogger"] = {
    "level": 'INFO',
}
# Plugins to include
config["Plugins"] = {
    "serializer": 'yes',
    "validator": 'yes',
    "reporter": 'yes',
    "docker": 'yes',
    "renderer": 'no',
    "jupyter": 'yes'
}
