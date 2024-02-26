# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from utils import *
import pytest


@pytest.fixture(params=[1, 2, 3])
def dim(request):
    return request.param


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


def test_convert_array_notation(parser, dim):
    """
    Test that :func:`convert_array_notation` successfully converts an implied
    array range assignment into an explicit one.
    """
    schedule = get_schedule(parser, implied_array_assignment[dim])
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Range)) == 0
    convert_array_notation(schedule)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Range)) == dim
    assert str(schedule) == str(get_schedule(parser, array_assignment[dim]))


def test_avoid_array_notation_subroutine(parser):
    """
    Test that :func:`convert_array_notation` does not use array notation in
    subroutine calls.
    """
    schedule = get_schedule(parser, cs.subroutine_call)
    assert len(schedule.walk(nodes.Call)) == 1
    assert len(schedule.walk(nodes.Range)) == 0
    convert_array_notation(schedule)
    assert len(schedule.walk(nodes.Call)) == 1
    assert len(schedule.walk(nodes.Range)) == 0


def test_convert_range_loops(parser, dim):
    """
    Test that :func:`convert_range_loops` successfully converts an array range
    assignment into a loop. If dim > 1 then the loop should itself contain an
    array range assignment.
    """
    schedule = get_schedule(parser, array_assignment[dim])
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Loop)) == 0
    convert_range_loops(schedule)
    assert len(schedule.walk(nodes.Assignment)) == 1
    assert len(schedule.walk(nodes.Loop)) == dim
