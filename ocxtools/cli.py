#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""generator CLI commands."""

# System imports
from __future__ import annotations
import sys
# Third party
from click import pass_context
from click_shell import shell
import typer
from loguru import logger

# Project imports
from ocxtools import __app_name__, __version__
import ocxtools.serializer.cli
import ocxtools.validator.cli
import ocxtools.docker.cli
import ocxtools.reporter.cli
import ocxtools.renderer.cli
import ocxtools.reporter.cli
from ocxtools.console.console import CliConsole
from ocxtools.context.context_manager import ContextManager
from ocxtools.config import config

LOG_FILE = config.get('FileLogger', 'log_file')
RETENTION = config.get('FileLogger', 'retention')
ROTATION = config.get('FileLogger', 'rotation')
SINK_LEVEL = config.get('FileLogger', 'level')
if DEBUG := config.getboolean('Defaults', 'debug'):
    SINK_LEVEL = 'DEBUG'
STDOUT_LEVEL = config.get('StdoutLogger', 'level')
COMMAND_HISTORY = config.get('Defaults', 'command_history')
EDITOR = config.get('Defaults', 'text_editor')

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
log_config = {
    "handlers": [
        # {"sink": sys.stdout, "format": "{time} - {message}"},
        {"sink": LOG_FILE, "serialize": False,
         "retention": RETENTION,
         "rotation": ROTATION,
         "level": SINK_LEVEL},
    ],
}
logger.remove()  # Remove all handlers added so far, including the default one.
logger.add(sys.stderr, level=STDOUT_LEVEL)
logger.configure(**log_config)
logger.level(STDOUT_LEVEL)


# Function to capture warnings and log them using Loguru
# Custom warning handler
def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
    """
    Custom warning formatter.
    Args:
        message:
        category:
        filename:
        lineno:
        file:
        line:
    """
    # Log the warning using Loguru
    logger.warning("Custom Warning: {}:{} - {}", filename, lineno, message)


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
    ctx.obj = context_manager
    ctx.call_on_close(exit_cli)


@cli.command(short_help="Print the ocxtools version number.")
def version():
    """Print the ``ocxtools`` version number"""
    console.info(__version__)


@cli.command(short_help="Clear the console window.")
def clear():
    """Clear the console window"""
    command = f'"cmd /c {clear}"'
    result = typer.launch(command)
    typer.echo(result)


# @cli.command(short_help="Load a new app configuration.")
# def load_config():
#     """Load a new app configuration."""
#     config.read()
#
#
# @cli.command()
# def save_config():
#     # Save the config file
#     with open(f'{__app_name__}.ini', 'w') as configfile:
#         config.write(configfile)
#


# Arrange all command groups from Typer
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
