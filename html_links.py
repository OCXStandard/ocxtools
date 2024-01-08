#  Copyright (c) 2024. OCX Consortium https://3docx.org. See the LICENSE

# Insert correct href links in ocxtool.html

from pathlib import Path
import re


# Define a function to be used as a replacement
def replace_md_with_html(match):
    return match.group(1) + 'html' + match.group(3)


def remove_directory_from_path(match):
    return match.group(1) + match.group(3) + match.group(4)


def insert_links():
    """Insert links to readme sub-pages"""

    ocxtools_html = Path('readme/ocxtools.html')
    content = ocxtools_html.read_text(encoding='utf-8')
    # Define a regular expression pattern to match href attributes with .md extension
    pattern = r'(<a\s+href=".*?\.)(md)(".*?>)'
    # Use re.sub() to perform the replacement from .md to .html
    modified_html_content = re.sub(pattern, replace_md_with_html, content)
    # Remove the parent directory
    pattern = r'(<a\s+href=")(.*\/)?(.*?\.html)(".*?>)'
    modified_html_content = re.sub(pattern, remove_directory_from_path, modified_html_content)
    ocxtools_html.write_text(modified_html_content, encoding='utf-8')


insert_links()
