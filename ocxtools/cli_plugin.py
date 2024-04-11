#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""CLI plugin method"""
from typing import Any, List, Tuple

import typer
from typer import Typer

# Project imports
from ocxtools.loader.loader import DynamicLoader, ModuleDeclaration


def cli_plugin(app_name: str, app: Typer) -> Tuple[str, Any]:
    """
    ClI plugin

    Args:
        app: The Typer app
        app_name: the name of Typer the subcommand.

    Returns:
        The typer plug-in app object

    """
    typer_click_object = typer.main.get_command(app)
    return app_name, typer_click_object


class PluginManager:
    """
    Plugin manager for CLI sub commands
    """

    def __init__(self, package: str, cli: Any):
        self._package = package
        self._cli = cli

    def load_plugin(self, module: str, plugin: str = 'cli'):
        """
        Load a plugin module
        Args:
            module: The module containing the plugin
            plugin: The plugin name
        """
        declaration = ModuleDeclaration(self._package, module, plugin)
        loader = DynamicLoader()
        return loader.import_module(declaration)

    def load_plugins(self, plugins: List):
        """Load all the plugins"""

        for app in plugins:
            cli_module = self.load_plugin(app)
            subcommand, typer_click_object = cli_module.cli_plugin()
            self._cli.add_command(typer_click_object, subcommand)
