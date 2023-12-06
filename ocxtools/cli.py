#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""generator CLI commands."""
# System imports
from __future__ import annotations
import sys
import warnings
# Third party
from click import clear, pass_context, secho
from click_shell import shell, Shell

from loguru import logger
from rich import print
from typing import Union, Optional, Type, Callable
# Project imports
from ocxtools import WIKI_URL
import ocxtools.serializer.cli
import ocxtools.validator.cli
import ocxtools.docker.cli
from ocxtools.console.console import CliConsole
from ocxtools.context.context_manager import ContextManager

# Project
from ocxtools import __app_name__, __version__

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
config = {
    "handlers": [
        # {"sink": sys.stdout, "format": "{time} - {message}"},
        {"sink": f"{__app_name__}.log", "serialize": False},
    ],
}
logger.remove()  # Remove all handlers added so far, including the default one.
logger.add(sys.stderr, level="WARNING")
logger.configure(**config)
logger.level("WARNING")


# Function to capture warnings and log them using Loguru
# Custom warning handler
def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
    # Log the warning using Loguru
    logger.warning("Custom Warning: {}:{} - {}", filename, lineno, message)

def capture_warnings(record, ):
    """
    Capture python warnings
    Args:
        record: python warning record
    """
    logger.warning("Captured warning: {}", record.message)


# Attach the capture_warnings function to the warnings module
warnings.showwarning = custom_warning_handler

# Generate a sample warning
warnings.warn("This is a sample warning")


def exit_cli():
    """
    Override exit method
    """
    logger.info(f"{__app_name__} session finished.")


# Create the Console and ContextManager instances
console = CliConsole()
context_manager = ContextManager()


class OcxShell(Shell):
    def __init__(
            self,
            prompt: Optional[Union[str, Callable[..., str]]] = None,
            intro: Optional[str] = None,
            hist_file: Optional[str] = None,
    ):
        super().__init__(prompt=prompt, intro=intro, hist_file=hist_file)


@shell(prompt=f"{__app_name__} >: ", intro=f"Starting {__app_name__}...")
@pass_context
def cli(ctx):
    """
    Main CLI
    """

    console.print(LOGO)
    console.print(f"Version: {__version__}")
    console.print("Copyright (c) 2023. OCX Consortium https://3docx.org\n")
    logger.info(f"{__app_name__} session started.")
    ctx.call_on_close(exit_cli)
    ctx.obj = context_manager


@cli.command(short_help="Clear the screen")
def clear():
    """Clear the console window."""
    # clear()


# Arrange all command groups from Typer
subcommand, typer_click_object = ocxtools.serializer.cli.cli_plugin()
cli.add_command(typer_click_object, subcommand)
subcommand, typer_click_object = ocxtools.validator.cli.cli_plugin()
cli.add_command(typer_click_object, subcommand)
subcommand, typer_click_object = ocxtools.docker.cli.cli_plugin()
cli.add_command(typer_click_object, subcommand)
