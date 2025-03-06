#!/usr/bin/bash

# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

mkdir -p outputs
psyclone  -s demo3_loop.py -o outputs/demo3_loop-double_loop.F90 \
        fortran/double_loop.F90
