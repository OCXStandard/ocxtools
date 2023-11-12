#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""generator CLI commands."""
# System imports
from __future__ import annotations
import sys

# Third party
import typer
from typing_extensions import Annotated
from loguru import logger
from click_shell import shell
from click import pass_context, clear, secho

# Project
from ocxtools import __version__, __app_name__

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
        {"sink": sys.stdout, "format": "{time} - {message}"},
        {"sink": str.join(__name__, ".log"), "serialize": True},
    ],
}


def exit_cli():
    logger.info(f'{__app_name__} session finished.')


@shell(prompt=f"{__app_name__} >: ", intro=f"Starting {__app_name__}...")
@pass_context
def cli(ctx):
    """
    Main CLI
    """

    secho(LOGO, fg='blue')
    secho(f"Version: {__version__}", fg='green')
    secho("Copyright (c) 2023. OCX Consortium https://3docx.org\n", fg='green')
    logger.info(f'{__app_name__} session started.')
    ctx.call_on_close(exit_cli)


@cli.command(short_help="Clear the screen")
def clear():
    """Clear the console window."""
    clear()


if __name__ == "__main__":
    cli(prog_name=__app_name__)
