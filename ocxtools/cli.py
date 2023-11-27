#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""generator CLI commands."""
# System imports
from __future__ import annotations

import sys

# Third party
from click import clear, pass_context, secho
from click_shell import shell
from loguru import logger

import ocxtools.serializer.cli
import ocxtools.validator.cli

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
logger.level("INFO")


def exit_cli():
    logger.info(f"{__app_name__} session finished.")


@shell(prompt=f"{__app_name__} >: ", intro=f"Starting {__app_name__}...")
@pass_context
def cli(ctx):
    """
    Main CLI
    """

    secho(LOGO, fg="blue")
    secho(f"Version: {__version__}", fg="green")
    secho("Copyright (c) 2023. OCX Consortium https://3docx.org\n", fg="green")
    logger.info(f"{__app_name__} session started.")
    ctx.call_on_close(exit_cli)


@cli.command(short_help="Clear the screen")
def clear():
    """Clear the console window."""
    # clear()


# Arrange all command groups from Typer
subcommand, typer_click_object = ocxtools.serializer.cli.cli_plugin()
cli.add_command(typer_click_object, subcommand)
subcommand, typer_click_object = ocxtools.validator.cli.cli_plugin()
cli.add_command(typer_click_object, subcommand)
