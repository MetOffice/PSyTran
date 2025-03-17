#!/usr/bin/bash

# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

mkdir -p ${VIRTUAL_ENV}/share/psyclone
PSYCLONE_CFG=$(python3 -c """
import psyclone
import os
for path in psyclone.__path__:
    cfg = os.path.join(path, '..', '..', 'config', 'psyclone.cfg')
    if os.path.exists(cfg):
        print(cfg)
        break
""")
if [ -z ${PSYCLONE_CFG} ]
then
        echo "Could not find a 'psyclone.cfg' file to use as default."
        curl -OL https://raw.githubusercontent.com/stfc/PSyclone/master/config/psyclone.cfg
        mv psyclone.cfg ${VIRTUAL_ENV}/share/psyclone
else
        cp ${PSYCLONE_CFG} ${VIRTUAL_ENV}/share/psyclone
fi
