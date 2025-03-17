.. (C) Crown Copyright 2023, Met Office. All rights reserved.

   This file is part of PSyTran and is released under the BSD 3-Clause license.
   See LICENSE in the root of the repository for full licensing details.

Welcome to PSyTran's documentation!
==================================

PSyTran is a Python package for streamlining OpenMP and OpenACC CPU/GPU porting
efforts using the `PSyclone <https://github.com/stfc/PSyclone>`__
domain-specific compiler and code transformation tool.

Before getting started with PSyTran, it is recommended that you familiarise yourself
with the following background material:

* `OpenACC website <https://www.openacc.org>`__.
* `OpenMP website <https://www.openmp.org>`__.
* `PSyclone documentation <https://psyclone.readthedocs.io/en/stable>`__.

API documentation
-----------------

The API documentation page shows the objects comprising PSyTran.

.. toctree::
    :maxdepth: 1

    API documentation <psytran>

Alternatively, an alphabetical list can be found on the :ref:`index <genindex>` page.
A :ref:`search engine <search>` is also provided.

Demos
-----

The best way to learn about PSyTran is by doing! The following examples demonstrate how
to use PSyTran to complete standard OpenACC and OpenMP porting tasks, such as inserting
directives and clauses.

.. toctree::
    :maxdepth: 1

    1. Basic usage <demos/demo1_psyclone.py>
    2. Inserting kernels directives <demos/demo2_kernels.py>
    3. Inserting loop directives <demos/demo3_loop.py>
    4. Adding collapse clauses <demos/demo4_collapse.py>
