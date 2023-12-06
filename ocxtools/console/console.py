#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""CLI console"""

# System imports
from enum import Enum
from typing import List
import subprocess
# Third party imports
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

# Project imports
from rich.style import Style

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


class CliConsole:
    """
    CLI console
    """

    def __init__(self):
        self.console = Console(theme=console_theme)

    def print_table(self, table: Table, justify: Justify = Justify.CENTER):
        """
        Console table print method
        Args:
            justify: Justify the table in the console. Default = ``center``
            table: A Rich Table to output.
        """
        self.console.print("\n")
        self.console.print(table, justify=justify.value)
        self.console.print("\n")

    def print_table_row(self, table: Table, cells: List, justify: Justify = Justify.CENTER):
        """
        Console table print method
        Args:
            justify: Justify the table in the console. Default = ``center``
            table: A Rich Table to output.
        """
        table.add_row(*[str(cell) for cell in cells])
        self.console.print(table, justify=justify.value, show_header=False)

    def print_error(self, msg: str):
        """
        Console error print method
        Args:
            msg: Output message
        """
        text = f'{msg}'
        self.console.print(f':cross_mark:{PADDING}{msg}', style="error")

    def print(self, msg: str):
        """
        Console info print method
        Args:
            msg: Output message
        """
        self.console.print(f':information:{PADDING}{msg}', style="info")

    def print_warning(self, msg: str):
        """
        Console info print method
        Args:
            msg: Output message
        """
        self.console.print(f':warning:{PADDING}{msg}', style="warning")

    def print_section(self, title: str, separator: str = "=", style: Style = style_section):
        """

        Args:
            style: The rule style
            separator: The rule characters
            title: The section title
        """
        self.console.rule(title=f'[bold black]{title}[/bold black]', characters=separator, style=style)

    def run_sub_process(self, command: str):
        """
        Execute the command in a python subprocess.
        Args:
            command: The command to execute.
        """
        # Use subprocess.run to execute the command and capture output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            self.print(f"Command output:\n{result.stdout}")
        else:
            self.print_error(f"Command failed with error:\n{result.stderr}")
