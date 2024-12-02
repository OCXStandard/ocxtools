#  Copyright (c) 2022. OCX Consortium https://3docx.org. See the LICENSE

import os
import sys

from loguru import logger

# To make sure that the tests import the modules this has to come before the import statements
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

logger.disable("ocxtools")
SCHEMA_VERSION = '3.0.0'
MODEL1 = 'NAPA-OCX_M1.3docx'
MODEL2 = 'NAPA-OCX_M2.3docx'
MODEL3 = 'NAPA-OCX_M3.3docx'
MODEL4 = 'NAPA-OCX_M4.3docx'
MODEL5 = 'NAPA-OCX_M5.3docx'
MODEL6 = 'NAPA-OCX_M6.3docx'
MODEL7 = 'NAPA-OCX_M7.3docx'
MODEL8 = 'NAPA-OCX_M8.3docx'
AVEVA = 'AVEVA-E3D-Model01.3docx'
TEST_MODEL = MODEL1
