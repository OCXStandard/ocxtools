#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Docker CLI."""
# System imports
from pathlib import Path
from typing import Any, Tuple

import click
# 3rd party imports
from loguru import logger
import typer

from typing_extensions import Annotated

# Project imports
from ocxtools import DOCKER_IMAGE, DOCKER_CONTAINER, DOCKER_DESKTOP
from ocxtools.console.console import CliConsole

docker = typer.Typer()

console = CliConsole()



@docker.command()
def run(
        container: Annotated[str, typer.Option(help="The docker port number")] = DOCKER_CONTAINER,
        docker_port: Annotated[int, typer.Option(help="The docker port number")] = 8080,
        public_port: Annotated[int, typer.Option(help="The docker port number")] = 8080,
        image: Annotated[str, typer.Option(help="The docker image")] = DOCKER_IMAGE,
        tag: Annotated[str, typer.Option(help="The docker image tag")] = 'latest',
        pull: Annotated[str, typer.Option(help="The docker pull policy")] = 'always',
):
    console.run_sub_process(
        f'docker run -d --name {container} --pull {pull} -p {docker_port}:{public_port}  {image}:{tag}')
    check()

@docker.command()
def check(
 ):
    console.run_sub_process('docker ps')


@docker.command()
def stop(
        container: Annotated[str, typer.Option(help="The container name")] = DOCKER_CONTAINER,
):
    console.run_sub_process(f'docker stop {container}')
    console.run_sub_process(f'docker rm {container}')


def cli_plugin() -> Tuple[str, Any]:
    """
    ClI plugin

    Returns the typer command object
    """
    typer_click_object = typer.main.get_command(docker)
    return "docker", typer_click_object
