#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Docker CLI."""
# System imports
from typing import Any, Tuple
# 3rd party imports
import typer
from typing_extensions import Annotated

# Project imports
from ocxtools import DOCKER_IMAGE, DOCKER_CONTAINER, DOCKER_DESKTOP, DOCKER_TAG, DOCKER_PORT
from ocxtools.context.context_manager import get_context_manager
from ocxtools.docker import __app_name__

docker = typer.Typer()


@docker.command()
def run(
        container: Annotated[str, typer.Option(help="The docker port number")] = DOCKER_CONTAINER,
        docker_port: Annotated[int, typer.Option(help="The docker port number")] = DOCKER_PORT,
        public_port: Annotated[int, typer.Option(help="The docker port number")] = DOCKER_PORT,
        image: Annotated[str, typer.Option(help="The docker image")] = DOCKER_IMAGE,
        tag: Annotated[str, typer.Option(help="The docker image tag")] = DOCKER_TAG,
        pull: Annotated[str, typer.Option(help="The docker pull policy")] = 'always',
):
    """Start the docker validator container."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.run_sub_process(
        f'docker run -d --name {container} --pull {pull} -p {docker_port}:{public_port}  {image}:{tag}')
    check()


@docker.command()
def check(
):
    """Check the status of the docker validator container."""
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
    """Sow the docker readme with usage examples."""
    context_manager = get_context_manager()
    console = context_manager.get_console()
    console.readme(__app_name__)


@docker.command()
def stop(
        container: Annotated[str, typer.Option(help="The container name")] = DOCKER_CONTAINER,
):
    "Stop and remove the validator container."
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
