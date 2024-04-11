#  Copyright (c) 2022. OCX Consortium https://3docx.org. See the LICENSE

import os
import sys

from loguru import logger

# To make sure that the tests import the modules this has to come before the import statements
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

logger.disable("ocxtools")
SCHEMA_VERSION = '3.0.0rc3'
MODEL1 = 'NAPA-OCX_M1_v300rc3.3docx'
MODEL2 = 'NAPA-OCX_M2_v300rc3.3docx'
MODEL3 = 'NAPA-OCX_M3_v300rc3.3docx'
MODEL4 = 'NAPA-OCX_M4_v300rc3.3docx'
MODEL5 = 'NAPA-OCX_M5_v300rc3.3docx'
MODEL6 = 'NAPA-OCX_M6_v300rc3.3docx'
MODEL7 = 'NAPA-OCX_M7_v300rc3.3docx'
MODEL8 = 'NAPA-OCX_M8_v300rc3.3docx'
TEST_MODEL = MODEL1
