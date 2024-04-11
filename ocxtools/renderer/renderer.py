#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
""" Render classes"""

from enum import Enum
from pathlib import Path
# System imports
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger
from lxml import etree
from rich.table import Table
from rich.tree import Tree
# Third party imports
from tabulate import tabulate

from ocxtools.console.console import style_table_header
from ocxtools.exceptions import SourceError
# Project imports
from ocxtools.utils.utilities import SourceValidator


class TreeNode:
    """
    Represents a node in a tree structure.

    Args:
        name: The name of the node.

    Attributes:
        name: The name of the node.
        children: A list of child nodes.
    """

    def __init__(self, name):
        self.name = name
        self.children = []


class RenderError(ValueError):
    """Render errors."""


class ReportType(Enum):
    """Validator report types"""
    OCX = 'ocx'
    SCHEMATRON = 'schematron'


class TableRender:
    @staticmethod
    def render(data: Dict):
        """

        Args:
            data:

        Returns:

        """
        headers = []
        values = []
        for k, v in data.items():
            headers.append(k)
            values.append(v)
        return tabulate([headers, values], headers="firstrow")


class RichTable:
    """Build a Rich table."""

    @classmethod
    def render(cls, title: str, data: List, show_header: bool = True, caption: str = None):
        """
        Render a rich table
        Args:
            show_header: If True render the table header.
            title: The table title rendered above.
            data: The table content. List of dictionaries where each dictionary
            represents a row in the table, and the keys represent column headers.
            caption: The table caption rendered below.

        Returns:
            The table
        """
        try:
            table = Table(title=title, header_style=style_table_header, caption=caption, show_header=show_header)
            headers = list(data[0].keys())
            for header in headers:
                table.add_column(header)
            for row in data:
                table.add_row(*[str(row[header]) for header in headers])
            return table
        except ValueError as e:
            logger.error(e)
            raise RenderError(e) from e

    @classmethod
    def df_to_table(cls,
                    pandas_dataframe: pd.DataFrame,
                    rich_table: Table,
                    show_index: bool = True,
                    index_name: Optional[str] = None,
                    ) -> Table:
        """Convert a pandas.DataFrame obj into a rich.Table obj.
        Args:
            pandas_dataframe (DataFrame): A Pandas DataFrame to be converted to a rich Table.
            rich_table (Table): A rich Table that should be populated by the DataFrame values.
            show_index (bool): Add a column with a row count to the table. Defaults to True.
            index_name (str, optional): The column name to give to the index column. Defaults to None, showing no value.
        Returns:
            Table: The rich Table instance passed, populated with the DataFrame values."""

        if show_index:
            index_name = str(index_name) if index_name else ""
            rich_table.add_column(index_name)

        for column in pandas_dataframe.columns:
            rich_table.add_column(str(column))

        for index, value_list in enumerate(pandas_dataframe.values.tolist()):
            row = [str(index)] if show_index else []
            row += [str(x) for x in value_list]
            rich_table.add_row(*row)

        return rich_table

    @classmethod
    def tree(cls, data: Dict, title: str) -> Tree:
        """
        Builds and renders a rich tree structure based on the provided data.

        Args:
            data: The dictionary representing the tree structure.
            title: The title of the tree.

        Returns:
            Tree: The rendered rich tree structure.
        """
        tree = Tree(f"[bold]{title}[/bold]")
        tree = cls.build_rich_tree(data, parent=tree)
        return tree

    @classmethod
    def build_rich_tree(cls, tree: Dict, parent: Tree) -> Tree:
        """
        Recursively builds a tree structure from a dictionary.

        Args:
            tree_dict: The dictionary representing the tree structure.
            parent: The parent node of the current tree level. Defaults to None for the root node.

        Returns:
            TreeNode: The root node of the built tree.
        """
        for child in tree:
            if len(tree[child]) > 0:
                cls.build_rich_tree(tree[child], parent)
            else:
                parent = parent.add(child)
        return parent

    @classmethod
    def render_rich_tree(cls, node, tree=None, depth=0):
        """
        Renders a rich tree structure based on the provided node.

        Args:
            node: The root node of the tree structure.
            tree: Optional existing Tree object to append the rendered tree. Defaults to None.
            depth: The current depth of the tree. Defaults to 0.

        Returns:
            Tree: The rendered rich tree structure.
        """
        tree = Tree(f"[bold]{node.name}[/bold]")
        for child in node.children:
            sub_tree = cls.render(child)
            tree.add(sub_tree)
        return tree


class XsltTransformer:
    """
        Transform an XML file using an xslt stylesheet.
    """

    def __init__(self, xslt_file: str):
        try:
            self._xslt_file = SourceValidator.validate(xslt_file)
        except SourceError as e:
            raise RenderError(e) from e

    def render(self, data: str, source_file: str, output_folder: str,
               report_type: ReportType = ReportType.SCHEMATRON) -> str:
        """

        Args:
            report_type: The report type. ``OCX`` or ``SCHEMATRON``.
            output_folder: The report folder.
            data: the xml data as a string
            source_file: The source file

        Returns:
            The path to the output file name
        """
        # Parse XML and XSLT files
        file_name = Path(source_file).stem
        output_file = Path(output_folder) / f'{file_name}_{report_type.value}_report.html'
        xml_file = Path(output_folder) / f'{file_name}.xml'
        with xml_file.open('w') as f:
            f.write(data)

        xml_tree = etree.parse(xml_file)
        xslt_tree = etree.parse(self._xslt_file)

        # Create an XSLT processor
        transform = etree.XSLT(xslt_tree)

        # Apply the transformation
        result_tree = transform(xml_tree)

        # Save the result to a new file
        result_tree.write(output_file, pretty_print=True, encoding='utf-8')

        return str(output_file)
