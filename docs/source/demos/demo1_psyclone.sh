#!/usr/bin/bash

# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

mkdir -p outputs
psyclone -s ./demo1_psyclone.py -o outputs/demo1_psyclone-empty.F90 \
        fortran/empty.F90
