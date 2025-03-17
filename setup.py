# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from setuptools import setup
import sys

if sys.version_info[0] != 3:
    raise Exception("Requires Python 3.")

setup(
    name="psytran",
    version="0.1",
    description=(
        "PSyTran: Tools for automating OpenACC GPU porting efforts using"
        " PSyclone"
    ),
    author="Joe Wallwork",
    author_email="joseph.wallwork@metoffice.gov.uk",
    packages=["psytran"],
)
