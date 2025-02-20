# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for PSyACC's `convert` module.
"""

from psyclone.psyir import nodes
from utils import get_schedule

import code_snippets as cs
from psyacc.convert import convert_array_notation

array_assignment = {
    1: cs.array_assignment_1d,
    2: cs.array_assignment_2d,
    3: cs.array_assignment_3d,
}

implied_array_assignment = {
    1: cs.implied_array_assignment_1d,
    2: cs.implied_array_assignment_2d,
    3: cs.implied_array_assignment_3d,
}


def test_convert_array_notation(fortran_reader, dim):
    """
    Test that :func:`convert_array_notation` successfully converts an implied
    array range assignment into an explicit one.
    """
    schedule = get_schedule(fortran_reader, implied_array_assignment[dim])
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Range)) == 0
    convert_array_notation(schedule)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Range)) == dim
    assert str(schedule) == str(
        get_schedule(fortran_reader, array_assignment[dim])
    )


def test_avoid_array_notation_subroutine(fortran_reader):
    """
    Test that :func:`convert_array_notation` does not use array notation in
    subroutine calls.
    """
    schedule = get_schedule(fortran_reader, cs.subroutine_call)
    assert len(schedule.walk(nodes.Call)) == 1
    assert len(schedule.walk(nodes.Range)) == 0
    convert_array_notation(schedule)
    assert len(schedule.walk(nodes.Call)) == 1
    assert len(schedule.walk(nodes.Range)) == 0
