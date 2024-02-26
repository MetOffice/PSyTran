# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyacc.assignment import is_literal_assignment
from utils import *


def test_is_literal_assignment(parser):
    """
    Test that a :func:`is_literal_assignment` correctly determines a node
    corresponding to the assignment of a literal value.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    assert not is_literal_assignment(schedule.walk(nodes.Loop)[0])
    assert is_literal_assignment(schedule.walk(nodes.Assignment)[0])


def test_is_not_literal_assignment(parser):
    """
    Test that a :func:`is_literal_assignment` correctly determines a node
    not corresponding to the assignment of a literal value.
    """
    schedule = get_schedule(
        parser, cs.loop_with_1_assignment_and_intrinsic_call
    )
    assert not is_literal_assignment(schedule.walk(nodes.Assignment)[0])
