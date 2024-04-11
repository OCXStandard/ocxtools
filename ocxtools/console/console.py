#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""CLI console"""

# System imports


import subprocess
from enum import Enum
from pathlib import Path
from typing import List, Union

from loguru import logger
# Third party imports
from rich.console import Console
from rich.markdown import Markdown
from rich.style import Style
from rich.table import Table
from rich.theme import Theme

from ocxtools import config
# Project imports
from ocxtools.utils.utilities import get_file_path

# # Defaults
README_FOLDER = config.get("Defaults", "readme_folder")

console = Console()

# Styling

PADDING = f'{" " * 5}'
console_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red"
})

style_table_header = Style(color="blue", bold=True)
style_section = Style(color="blue", bold=True)


class Justify(Enum):
    """Justify enum"""
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    FULL = "full"


class CliConsole(Console):
    """
    CLI console
    """

    def __init__(self):
        super().__init__(theme=console_theme)

    def print_table(self, table: Table, justify: Justify = Justify.CENTER):
        """
        Console table print method

        Args:
            justify: Justify the table in the console. Default = ``center``
            table: A Rich Table to output.

        """
        self.print("\n")
        self.print(table, justify=justify.value)
        self.print("\n")

    def print_table_row(self, table: Table, cells: List, justify: Justify = Justify.CENTER):
        """
        Console table print method

        Args:
            justify: Justify the table in the console. Default = ``center``
            table: A Rich Table to output.

        """
        table.add_row(*[str(cell) for cell in cells])
        self.print(table, justify=justify.value, show_header=False)

    def error(self, msg: str):
        """
        Console error print method

        Args:
            msg: Output message

        """
        self.print(f':cross_mark:{PADDING}{msg}', style="error")

    def info(self, msg: Union[str, Markdown]):
        """
        Console info print method

        Args:
            msg: Output message

        """
        self.print(f':information:{PADDING}{msg}', style="info")
        logger.info(msg)

    def warning(self, msg: str):
        """
        Console info print method

        Args:
            msg: Output message

        """
        self.print(f':warning:{PADDING}{msg}', style="warning")
        logger.warning(msg)

    def section(self, title: str, separator: str = "=", style: Style = style_section):
        """

        Args:
            style: The rule style
            separator: The rule characters
            title: The section title

        """
        self.rule(title=f'[bold black]{title}[/bold black]', characters=separator, style=style)

    def run_sub_process(self, command: str, silent:bool = False) -> str:
        """
        Execute the command in a python subprocess.

        Args:
            command: The command to execute.
            silent: If True, don't output anything to the console.

        """
        # Use subprocess.run to execute the command and capture output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        # Check if the command was successful
        if result.returncode != 0:
            self.error(f"Command failed with error:\n{result.stderr!r}")
            logger.error(f"Command {result.args!r} failed with error:\n{result.stderr!r}")
        else:
            logger.info(f"Command {result.args!r}: with return code{result.returncode}")
            if result.stderr == '':
                if not silent:
                    self.info(result.stdout)
                return result.stdout
            else:
                if not silent:
                    self.info(result.stderr)
                return result.stderr

    def readme(self, sub_command: str):
        """Print the ``sub_command`` readme file in the console window.

        Args:
            sub_command: The sub_command name
        """
        readme_file = f'{README_FOLDER}/{sub_command}.md'
        file_path = Path(get_file_path(readme_file))
        md = Markdown(file_path.read_text(encoding='utf-8'))
        self.print(md)

    def man_page(self, sub_command: str):
        """Display the ``sub_command`` html file in a browser.

        Args:
            sub_command: The sub_command name
        """
        readme_file = f'{README_FOLDER}/{sub_command}.html'
        file_path = Path(get_file_path(readme_file))
        self.run_sub_process(f'cmd /c start {file_path.resolve()}')

    def html_page(self, url: str):
        """Display the `a web page in a browser window.

        Args:
            url: The address to the web page
        """
        self.run_sub_process(f'cmd /c start {url}')
