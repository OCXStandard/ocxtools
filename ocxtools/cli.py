#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""generator CLI commands."""

# System imports
from __future__ import annotations

import logging
import warnings

import typer
# Third party
from click import pass_context
from click_shell import shell
from loguru import logger

import ocxtools.docker.cli
import ocxtools.jupyter.cli
import ocxtools.renderer.cli
import ocxtools.reporter.cli
import ocxtools.serializer.cli
import ocxtools.validator.cli
# Project imports
from ocxtools import __app_name__, __version__
from ocxtools.config import config
from ocxtools.console.console import CliConsole
from ocxtools.context.context_manager import ContextManager

LOG_FILE = config.get('FileLogger', 'log_file')
RETENTION = config.get('FileLogger', 'retention')
ROTATION = config.get('FileLogger', 'rotation')
SINK_LEVEL = config.get('FileLogger', 'level')
if DEBUG := config.getboolean('Defaults', 'debug'):
    SINK_LEVEL = 'DEBUG'
STDOUT_LEVEL = config.get('StdoutLogger', 'level')
COMMAND_HISTORY = config.get('Defaults', 'command_history')
EDITOR = config.get('Defaults', 'text_editor')
REGISTER_ISSUE = config.get('Defaults', 'register_issue')

# https://patorjk.com/software/taag/#p=testall&f=Graffiti&t=OCX-wiki
# Font: 3D Diagonal + Star Wars
LOGO = r"""
             ,----..
            /   /   \    ,----..   ,--,     ,--,
           /   .     :  /   /   \  |'. \   / .`|
          .   /   ;.  \|   :     : ; \ `\ /' / ;
         .   ;   /  ` ;.   |  ;. / `. \  /  / .'          ______   ___    ___   _     _____
         ;   |  ; \ ; |.   ; /--`   \  \/  / ./          |      | /   \  /   \ | |   / ___/
         |   :  | ; | ';   | ;       \  \.'  /     _____ |      ||     ||     || |  (   \_
         .   |  ' ' ' :|   : |        \  ;  ;     |     ||_|  |_||  O  ||  O  || |___\__  |
         '   ;  \; /  |.   | '___    / \  \  \    |_____|  |  |  |     ||     ||     /  \ |
          \   \  ',  / '   ; : .'|  ;  /\  \  \            |  |  |     ||     ||     \    |
           ;   :    /  '   | '/  :./__;  \  ;  \           |__|   \___/  \___/ |_____|\___|
            \   \ .'   |   :    / |   : / \  \  ;
             `---`      \   \ .'  ;   |/   \  ' |
                         `---`    `---'     `--`
"""

# Logging config for application
# Function to capture warnings and log them using Loguru
# Custom warning handler
# logger.remove()
showwarning_ = warnings.showwarning


def showwarning(message, *args, **kwargs):
    """
    Show warnings.
    Args:
        message:
        *args:
        **kwargs:
    """
    logger.warning(message)
    showwarning_(message, *args, **kwargs)


logger.add(LOG_FILE, level=SINK_LEVEL)
logger.remove()  # Remove all handlers added so far, including the default one.
warnings.simplefilter('default')
warnings.showwarning = showwarning
# Python main logger
# Attach the cli handler to the python warnings logger
logger.enable(__app_name__)
logger.enable('xsdata')
# py_warnings = logging.getLogger("py.warnings")
# py_warnings.handlers = [custom_warning_handler]
# py_warnings.propagate = True
logging.captureWarnings(True)

# logger.remove()  # Remove all handlers added so far, including the default one.
logger.add(LOG_FILE, level=SINK_LEVEL)
warnings.simplefilter('default')
warnings.showwarning = showwarning


def capture_warnings(record):
    """
    Capture python warnings
    Args:
        record: python warning record
    """
    logger.warning("Captured warning: {}", record.message)


# Attach the capture_warnings function to the warnings module
# warnings.showwarning = custom_warning_handler


def exit_cli():
    """
    Override exit method
    """
    logger.info(f"{__app_name__} session finished.")


# Create the Console and ContextManager instances
console = CliConsole()
context_manager = ContextManager(console=console, config=config)


@shell(prompt=f"{__app_name__} >: ", hist_file=COMMAND_HISTORY, intro=f"Starting {__app_name__}...")
@pass_context
def cli(ctx):
    """
    Main CLI
    """

    console.print(LOGO)
    console.print(f"Version: {__version__}")
    console.print("Copyright (c) 2024. OCX Consortium (https://3docx.org)\n")
    logger.info(f"{__app_name__} session started.")
    logger.info(f"Logging level is {SINK_LEVEL}")
    ctx.obj = context_manager
    ctx.call_on_close(exit_cli)


@cli.command()
def readme():
    """Show the README html page with usage examples."""
    console.man_page(__app_name__)


@cli.command(short_help="Print the ocxtools version number.")
def version():
    """Print the ``ocxtools`` version number"""
    console.info(__version__)


@cli.command(short_help="Clear the console window.")
def clear():
    """Clear the console window"""
    command = f'"cmd /c {clear}"'
    typer.launch(command)


@cli.command(short_help="Clear the console window.")
def issues():
    """Register an issue with the ocxtools CLI"""
    console.html_page(REGISTER_ISSUE)


# Install any command group plugins
if config.getboolean('Plugins', 'serializer'):
    subcommand, typer_click_object = ocxtools.serializer.cli.cli_plugin()
    cli.add_command(typer_click_object, subcommand)
if config.getboolean('Plugins', 'validator'):
    subcommand, typer_click_object = ocxtools.validator.cli.cli_plugin()
    cli.add_command(typer_click_object, subcommand)
if config.getboolean('Plugins', 'docker'):
    subcommand, typer_click_object = ocxtools.docker.cli.cli_plugin()
    cli.add_command(typer_click_object, subcommand)
if config.getboolean('Plugins', 'reporter'):
    subcommand, typer_click_object = ocxtools.reporter.cli.cli_plugin()
    cli.add_command(typer_click_object, subcommand)
if config.getboolean('Plugins', 'renderer'):
    subcommand, typer_click_object = ocxtools.renderer.cli.cli_plugin()
    cli.add_command(typer_click_object, subcommand)
if config.getboolean('Plugins', 'jupyter'):
    subcommand, typer_click_object = ocxtools.jupyter.cli.cli_plugin()
    cli.add_command(typer_click_object, subcommand)
