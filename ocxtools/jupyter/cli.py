#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Docker CLI."""
# System imports
import re
from typing import Any, Tuple

# 3rd party imports
import typer
from typing_extensions import Annotated

# Project imports
from ocxtools import config
from ocxtools.context.context_manager import get_context_manager
from ocxtools.docker.cli import run
from ocxtools.jupyter import __app_name__
from ocxtools.renderer.renderer import RichTable
from ocxtools.utils.utilities import SourceValidator

# Docker
DOCKER_DESKTOP = config.get("DockerSettings", "docker_desktop")

jupyter = typer.Typer(help="Commands for managing the docker jupyter lab notebook.")


def extract_jupyter_url_with_token(log_content: str, server_location: str) -> str:
    """
    Extract the Jupyter Notebook URL with token from the log content.

    Args:
        server_location: The jupyter server location
        log_content: The log content as a string.

    Returns:
        str: The Jupyter Notebook URL with token if found, otherwise None.

    """
    regex_pattern = rf'http://{server_location}:\d+/lab\?token=\w+'
    for line in log_content.split('\n'):
        if url_with_token := re.search(
                regex_pattern, line
        ):
            return url_with_token[0]


@jupyter.command()
def lab(
        folder: Annotated[str, typer.Option(help="Local mount target folder name.")] =
        config.get('JupyterSettings','mount_folder'),
        docker_mount: Annotated[str, typer.Option(help="Docker mount path.")] =
        config.get('JupyterSettings', 'jupyter_mount'),
        mount: Annotated[bool, typer.Option(help="Mount a local directory in the docker.")] = True
):
    """Run jupyter lab in a container."""
    run(
        container=config.get('JupyterSettings', 'container_name'),
        docker_port=config.get('JupyterSettings', 'docker_port'),
        public_port=config.get('JupyterSettings', 'docker_port'),
        tag=config.get('JupyterSettings', 'docker_tag'),
        image=config.get('JupyterSettings', 'docker_image'),
        mount=mount,
        local_folder=folder,
        docker_volume=docker_mount,
    )


@jupyter.command()
def notebook(

):
    """Open the jupyter lab notebook on the jupyter lab server"""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    command = f"docker logs {config.get('JupyterSettings', 'container_name')}"
    log = console.run_sub_process(command, silent=True)
    jupyter_url = extract_jupyter_url_with_token(log, server_location='127.0.0.1')
    if SourceValidator.is_url(jupyter_url):
        console.html_page(jupyter_url)
    else:
        console.info(f'The jupyter lab address was not found {jupyter_url!r}')


@jupyter.command()
def settings():
    """Show the jupyter lab container settings."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.section('Jupyter lab settings')
    data = dict(config.items('JupyterSettings'))
    table = RichTable.render(data=[data], title='Settings')
    console.print_table(table)


@jupyter.command()
def readme(
):
    """Show the jupyter html page with usage examples."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.man_page(__app_name__)


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(jupyter)
    return __app_name__, typer_click_object
