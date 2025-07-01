<!--
  (C) Crown Copyright 2023, Met Office. All rights reserved.

  This file is part of PSyTran and is released under the BSD 3-Clause license.
  See LICENSE in the root of the repository for full licensing details.
-->

# PSyTran: tools for PSyclone transformation scripting

## Introduction

Before introducing PSyTran, we should introduce
[PSyclone](https://github.com/stfc/PSyclone). PSyclone is a domain-specific
compiler and code transformation tool for earth system codes written in Fortran.
In code transformation mode (which is of main interest here), PSyclone can be
used to read in Fortran source code, along with a user-defined
*transformation script* (written in Python), which describes modifications to be
made to the source code. With these two ingredients, PSyclone converts the
source code to its internal *intermediate representation*, applies the
transformations, and then writes out the modified code.

Key examples of transformations to be applied to the input code are to
insert [OpenMP](https://www.openmp.org) and [OpenACC](https://www.openacc.org)
directives and clauses, providing instructions to compilers on how to
distribute work in parallel for CPU or GPU. PSyclone offers the ability to
inject these compiler directives into source code as a transformation.

The transformations possible with PSyclone aren't limited to inserting compiler
directives. From chunking loops to inlining routines, PSyclone has an enormous
selection of transformations, which are all
[documented here](https://psyclone.readthedocs.io/en/stable/transformations.html).

PSyTran is a Python package which provides various helper functions for using
PSyclone, most notably for, but not limited to, writing transformation scripts
for inserting OpenACC and OpenMP directives and clauses.

Amongst other things, PSyTran provides functionality for:
 * simplifying tree traversal in PSyclone's intermediate representation,
 * finding and analysing the structure of loops and loop nests,
 * applying OpenACC `kernels` and `loop` directives,
 * applying OpenACC clauses to `loop` directives,
 * applying OpenMP directives,
 * querying `Node` types.

## General user instructions

Instructions for installing PSyTran and building and viewing its documentation
may be found on the [Wiki page](https://github.com/MetOffice/psytran/wiki#general-users).

## Developer notes

Contributions are very welcome! However, please read PSyTran's
[Coding Practices](./wiki/Coding-practices) before commencing development work.

When you make your first contribution, make sure to add yourself to the
[contributors list](./CONTRIBUTORS.md).
