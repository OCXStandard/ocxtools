#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Docker CLI."""
# System imports
import re
from pathlib import Path
from typing import Any, Tuple

# 3rd party imports
import typer
from typing_extensions import Annotated

# Project imports
from ocxtools import config
from ocxtools.context.context_manager import get_context_manager
from ocxtools.docker import __app_name__

# Docker
DOCKER_DESKTOP = config.get("DockerSettings", "docker_desktop")

docker = typer.Typer(help="Commands for managing the docker OCX validator.")


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


@docker.command()
def run(
        container: Annotated[str, typer.Option(help="The container name.")] =
        config.get("DockerSettings", "container_name"),
        docker_port: Annotated[int, typer.Option(help="The docker port number.")] =
        int(config.get("DockerSettings", "docker_port")),
        public_port: Annotated[int, typer.Option(help="The docker public exposed port number.")] =
        int(config.get("DockerSettings", "docker_port")),
        image: Annotated[str, typer.Option(help="The docker image name. "
                                                "Pulled from DockerHub if not available in local repo.")] =
        config.get("DockerSettings", "docker_image"),
        tag: Annotated[str, typer.Option(help="The docker image tag.")] =
        config.get("DockerSettings", "docker_tag"),
        pull: Annotated[str, typer.Option(help="The docker pull policy.")] =
        'always',
        local_folder: Annotated[str, typer.Option(help="Local folder mount target.")] =
        'models',
        docker_volume: Annotated[str, typer.Option(help="The docker mount path")] =
        '/work',
        mount: Annotated[bool, typer.Option(help="Mount a local directory. "
                                                 "If true, the provided local folder is mounted.")] = False
):
    """Pull the container from docker hup and start the container."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    if mount:
        mount_folder = Path.cwd() / local_folder
        console.run_sub_process(
            f'docker run -d --name {container} --pull {pull} -p {docker_port}:{public_port}  '
            f'-v {mount_folder}:{docker_volume} {image}:{tag}')
    else:
        console.run_sub_process(
            f'docker run -d --name {container} --pull {pull} -p {docker_port}:{public_port}  {image}:{tag}')
    check()


@docker.command()
def check(
):
    """Check the status of the docker running containers."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.run_sub_process('docker ps -a')


@docker.command()
def start(
):
    """Start the docker Desktop (Windows only)."""
    command = f'"{DOCKER_DESKTOP}"'
    typer.launch(command)


@docker.command()
def readme(
):
    """Show the docker cli html page with usage examples."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.man_page(__app_name__)


@docker.command()
def stop(
        container: Annotated[str, typer.Option(help="The container name")] =
        config.get("DockerSettings", "container_name"),
):
    """Stop and remove a container."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.run_sub_process(f'docker stop {container}')
    console.run_sub_process(f'docker rm {container}')


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(docker)
    return __app_name__, typer_click_object
