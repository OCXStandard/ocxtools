#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""ocx_tools CLI entry point script."""
from ocxtools import __app_name__
from ocxtools.cli import cli


def main():
    cli(prog_name=__app_name__)


if __name__ == "__main__":
    main()
