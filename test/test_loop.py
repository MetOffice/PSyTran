# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyacc.loop import _check_loop
from utils import *
import pytest


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=["1_assign", "3_assigns", "if"])
def perfection(request):
    return request.param


@pytest.fixture(params=["before", "after", "if"])
def imperfection(request):
    return request.param


perfectly_nested_loop = {
    "1_assign": cs.loop_with_1_assignment,
    "1_assign_intrinsic_call": cs.loop_with_1_assignment_and_intrinsic_call,
    "3_assigns": cs.loop_with_3_assignments,
    "double_3_assigns": cs.double_loop_with_3_assignments,
    "double_cond_3_assigns": cs.double_loop_with_conditional_3_assignments,
    "if": cs.triple_loop_with_conditional_1_assignment,
}

imperfectly_nested_double_loop = {
    "before": cs.imperfectly_nested_double_loop_before,
    "after": cs.imperfectly_nested_double_loop_after,
    "if": cs.imperfectly_nested_double_loop_with_if,
}

imperfectly_nested_triple_loop = {
    "before": cs.imperfectly_nested_triple_loop1_before,
    "after": cs.imperfectly_nested_triple_loop1_after,
    "if": cs.imperfectly_nested_triple_loop1_with_if,
}

conditional_perfectly_nested_subloop = {
    "before": cs.imperfectly_nested_triple_loop1_before_with_if,
    "after": cs.imperfectly_nested_triple_loop1_after_with_if,
    "if": cs.conditional_imperfectly_nested_triple_loop1,
}


def test_check_loop_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`_check_loop` is called
    with something other than a :class:`Loop`.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    assignments = schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        _check_loop(assignments[0])


def test_is_outer_loop(parser, nest_depth):
    """
    Test that a :func:`is_outer_loop` correctly determines whether a loop is
    outer-most in its nest.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    assert is_outer_loop(loops[0])
    for i in range(1, nest_depth):
        assert not is_outer_loop(loops[i])


def test_is_perfectly_nested(parser, perfection):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    nested loop.
    """
    schedule = get_schedule(parser, perfectly_nested_loop[perfection])
    loops = schedule.walk(nodes.Loop)
    assert is_perfectly_nested(loops[0])
    assert is_parallelisable(loops[0])
    assert is_independent(loops[0])


def test_is_not_perfectly_nested_double(parser, imperfection):
    """
    Test that :func:`is_perfectly_nested` correctly identifies an imperfectly
    nested double loop.
    """
    schedule = get_schedule(
        parser, imperfectly_nested_double_loop[imperfection]
    )
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])
    assert not is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])


def test_is_not_perfectly_nested_triple(parser, imperfection):
    """
    Test that :func:`is_perfectly_nested` correctly identifies an imperfectly
    nested triple loop.
    """
    schedule = get_schedule(
        parser, imperfectly_nested_triple_loop[imperfection]
    )
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])
    assert not is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])


def test_is_not_perfectly_nested_double_2_loop(parser):
    """
    Test that :func:`is_perfectly_nested` correctly identifies an imperfectly
    nested double loop containing two loops.
    """
    schedule = get_schedule(parser, cs.double_loop_with_2_loops)
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])
    assert not is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])


def test_is_perfectly_nested_subnest(parser, imperfection):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    nested sub-nest.
    """
    schedule = get_schedule(
        parser, imperfectly_nested_triple_loop[imperfection]
    )
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])
    assert is_perfectly_nested(loops[1])
    assert is_parallelisable(loops[0])


def test_is_perfectly_nested_subnest_conditional(parser, imperfection):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    nested sub-nest with conditional.
    """
    schedule = get_schedule(
        parser, conditional_perfectly_nested_subloop[imperfection]
    )
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])
    assert is_perfectly_nested(loops[1])
    assert is_perfectly_nested(loops[2])


def test_is_perfectly_nested_subnest_index_array(parser):
    """
    Test that :func:`is_perfectly_nested` correctly identifies a perfectly
    nested sub-nest where an index array is used.
    """
    schedule = get_schedule(parser, cs.double_loop_with_index_array)
    loops = schedule.walk(nodes.Loop)
    assert not is_perfectly_nested(loops[0])
    assert is_perfectly_nested(loops[1])
    assert not is_parallelisable(loops[0])


def test_is_simple_loop_1_literal(parser, nest_depth):
    """
    Test that :func:`is_simple_loop` correctly identifies a simple loop with
    one literal assignment.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    assert is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])
    assert is_independent(loops[0])


def test_is_simple_loop_2_literals(parser):
    """
    Test that :func:`is_simple_loop` correctly identifies a simple loop with
    two literal assignments.
    """
    schedule = get_schedule(parser, cs.loop_with_2_literal_assignments)
    loops = schedule.walk(nodes.Loop)
    assert is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])
    assert is_independent(loops[0])


def test_is_not_simple_loop_references(parser):
    """
    Test that :func:`is_simple_loop` correctly identifies a perfectly nested
    loop with a reference assignment as non-simple.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loops = schedule.walk(nodes.Loop)
    assert not is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])


def test_get_loop_variable_name(parser):
    """
    Test that :func:`get_loop_variable_name` correctly determines loop variable
    names.
    """
    schedule = get_schedule(parser, cs.quadruple_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    for i, expected in enumerate(["l", "k", "j", "i"]):
        assert get_loop_variable_name(loops[i]) == expected


def test_get_loop_nest_variable_names(parser):
    """
    Test that :func:`get_loop_nest_variable_names` correctly determines all
    loop variable names in a nest.
    """
    schedule = get_schedule(parser, cs.quadruple_loop_with_1_assignment)
    indices = ["l", "k", "j", "i"]
    for i, loop in enumerate(schedule.walk(nodes.Loop)):
        assert get_loop_nest_variable_names(loop) == indices[i:]


def test_is_independent_valueerror(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`is_independent` is
    called with an imperfectly nested :class:`Loop`.
    """
    schedule = get_schedule(parser, cs.imperfectly_nested_double_loop_before)
    expected = "is_independent can only be applied to perfectly nested loops."
    with pytest.raises(ValueError, match=expected):
        is_independent(schedule.walk(nodes.Loop)[0])


def test_is_not_independent_double_loop(parser):
    """
    Test that :func:`is_independent` correctly identifies a dependent double
    loop.
    """
    schedule = get_schedule(parser, cs.dependent_double_loop)
    loops = schedule.walk(nodes.Loop)
    assert is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])
    assert not is_independent(loops[0])
    assert is_independent(loops[1])


def test_is_not_independent_triple_loop(parser):
    """
    Test that :func:`is_independent` correctly identifies a dependent triple
    loop.
    """
    schedule = get_schedule(parser, cs.dependent_triple_loop)
    loops = schedule.walk(nodes.Loop)
    assert is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])
    assert not is_independent(loops[0])
    assert is_independent(loops[1])
    assert is_independent(loops[2])


def test_is_not_independent_triple_subloop(parser):
    """
    Test that :func:`is_independent` correctly identifies a dependent triple
    loop.
    """
    schedule = get_schedule(parser, cs.dependent_triple_subloop)
    loops = schedule.walk(nodes.Loop)
    assert is_simple_loop(loops[0])
    assert is_parallelisable(loops[0])
    assert not is_independent(loops[0])
    assert is_perfectly_nested(loops[1])
    assert not is_independent(loops[1])
    assert is_independent(loops[2])
