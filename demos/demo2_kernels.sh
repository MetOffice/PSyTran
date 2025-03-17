#!/usr/bin/bash

# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

mkdir -p outputs
psyclone -s demo2_kernels.py -o outputs/demo2_kernels-single_loop.F90 \
        fortran/single_loop.F90
