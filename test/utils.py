# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Various utility functions for PSyACC's test suite.
"""

import code_snippets as cs
from psyacc import (
    has_collapse_clause,
    has_gang_clause,
    has_seq_clause,
    has_vector_clause)

__all__ = ["has_clause", "get_schedule", "simple_loop_code"]

has_clause = {
    "sequential": has_seq_clause,
    "gang": has_gang_clause,
    "vector": has_vector_clause,
    "collapse": has_collapse_clause,
}


def get_schedule(fortran_reader, code_string):
    """
    Given a snippet of test code written as a string, get the schedule of the
    (first) invoke it contains.

    :arg fortran_reader: PSyclone's fortran_reader fixture
    :arg code_string: the code to be parsed, as a string
    """
    return fortran_reader.psyir_from_source(code_string).children[0]


def simple_loop_code(depth):
    """
    Generate a code string containing a perfectly nested loop with a single
    assignment at the deepest level.

    :arg depth: number of loops in the nest
    """
    if depth == 1:
        return cs.loop_with_1_assignment
    if depth == 2:
        return cs.double_loop_with_1_assignment
    if depth == 3:
        return cs.triple_loop_with_1_assignment
    if depth == 4:
        return cs.quadruple_loop_with_1_assignment
    raise NotImplementedError
