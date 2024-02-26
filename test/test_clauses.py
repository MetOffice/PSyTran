# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective
from psyacc.clauses import _prepare_loop_for_clause
from utils import *
import pytest


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=["sequential", "gang", "vector", "collapse"])
def clause(request):
    return request.param


@pytest.fixture(params=[2, 3])
def collapse(request):
    return request.param


@pytest.fixture(params=["before", "after"])
def imperfection(request):
    return request.param


imperfectly_nested_triple_loop1 = {
    "before": cs.imperfectly_nested_triple_loop1_before,
    "after": cs.imperfectly_nested_triple_loop1_after,
}

imperfectly_nested_triple_loop2 = {
    "before": cs.imperfectly_nested_triple_loop2_before,
    "after": cs.imperfectly_nested_triple_loop2_after,
}


def test_prepare_loop_for_clause_no_kernels_error(parser):
    """
    Test that a :class:`ValueError` is raised when
    :func:`_prepare_loop_for_clause` is called without a kernels directive.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Cannot apply a loop clause without a kernels directive."
    with pytest.raises(ValueError, match=expected):
        _prepare_loop_for_clause(loops[0])


def test_prepare_loop_for_clause_no_loop_dir(parser):
    """
    Test that :func:`_prepare_loop_for_clause` is correctly applied when there
    is no loop directive.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    _prepare_loop_for_clause(loops[0])
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)


def test_no_loop_clause(parser, nest_depth, clause):
    """
    Test that a lack of each clause is correctly identified.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    for i in range(nest_depth):
        assert not has_clause[clause](loops[i])


def test_apply_loop_clause(parser, nest_depth, clause):
    """
    Test that each clause is correctly applied.
    """
    for i in range(nest_depth):
        schedule = get_schedule(parser, simple_loop_code(nest_depth))
        loops = schedule.walk(nodes.Loop)
        apply_kernels_directive(loops[0])
        if clause == "collapse":
            collapse = nest_depth - i
            if collapse == 1:
                expected = "Expected an integer greater than one, not 1."
                with pytest.raises(ValueError, match=expected):
                    apply_clause[clause](loops[i], collapse)
                continue
            apply_clause[clause](loops[i], collapse)
            assert loops[i].parent.parent.__getattribute__(clause) == collapse
        else:
            apply_clause[clause](loops[i])
            assert loops[i].parent.parent.__getattribute__(clause)
        assert has_clause[clause](loops[i])


def test_apply_loop_seq_gang_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_seq` is
    applied to a loop with a ``gang`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_gang(loops[0])
    expected = "Cannot apply seq to a loop with a gang clause."
    with pytest.raises(ValueError, match=expected):
        apply_loop_seq(loops[0])


def test_apply_loop_seq_vector_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_seq` is
    applied to a loop with a ``vector`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_vector(loops[0])
    expected = "Cannot apply seq to a loop with a vector clause."
    with pytest.raises(ValueError, match=expected):
        apply_loop_seq(loops[0])


def test_apply_loop_gang_seq_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_gang` is
    applied to a loop with a ``seq`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_seq(loops[0])
    expected = "Cannot apply gang to a loop with a seq clause."
    with pytest.raises(ValueError, match=expected):
        apply_loop_gang(loops[0])


def test_apply_loop_vector_seq_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_vector` is
    applied to a loop with a ``seq`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_seq(loops[0])
    expected = "Cannot apply vector to a loop with a seq clause."
    with pytest.raises(ValueError, match=expected):
        apply_loop_vector(loops[0])


def test_has_collapse_clause_no_kernels(parser):
    """
    Test that :func:`has_collapse_clause` returns ``False`` for a loop with no
    ``kernels`` directive.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_collapse_clause(loops[0])


def test_has_collapse_clause_kernels_no_loop(parser):
    """
    Test that :func:`has_collapse_clause` returns ``False`` for a loop with a
    ``kernels`` directive but no ``loop`` directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    assert not has_collapse_clause(loops[0])


def test_has_collapse_clause_loop_no_collapse(parser):
    """
    Test that :func:`has_collapse_clause` returns ``False`` for a loop with a
    ``loop`` directive but no ``collapse`` clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    assert not has_collapse_clause(loops[0])


def test_apply_loop_collapse_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_collapse`
    is called with a non-integer collapse.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    expected = "Expected an integer, not '<class 'float'>'."
    with pytest.raises(TypeError, match=expected):
        apply_loop_collapse(loops[0], 2.0)


def test_apply_loop_collapse_valueerror(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_collapse`
    is called with an invalid collapse.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    expected = "Expected an integer greater than one, not 1."
    with pytest.raises(ValueError, match=expected):
        apply_loop_collapse(loops[0], 1)


def test_apply_loop_collapse_too_large_error(parser):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_collapse`
    is called with too large a collapse.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    expected = "Cannot apply collapse to 3 loops in a sub-nest of 2."
    with pytest.raises(ValueError, match=expected):
        apply_loop_collapse(loops[0], 3)


def test_apply_loop_collapse(parser, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a full nest.
    """
    schedule = get_schedule(parser, simple_loop_code(collapse))
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    apply_loop_collapse(loops[0], collapse)
    assert loops[0].parent.parent.collapse == collapse
    for loop in loops:
        assert has_collapse_clause(loop)


def test_apply_loop_collapse_subnest(parser, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a sub-nest.
    """
    schedule = get_schedule(parser, simple_loop_code(collapse + 1))
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    apply_loop_directive(loops[-1])
    apply_loop_collapse(loops[0], collapse)
    assert loops[0].parent.parent.collapse == collapse
    for i in range(collapse):
        assert has_collapse_clause(loops[i])
    assert loops[-1].parent.parent.collapse is None
    assert not has_collapse_clause(loops[-1])


def test_apply_loop_collapse_default(parser, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a full nest
    when the `collapse` keyword argument is not used.
    """
    schedule = get_schedule(parser, simple_loop_code(collapse))
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    apply_loop_collapse(loops[0])
    assert loops[0].parent.parent.collapse == collapse
    for loop in loops:
        assert has_collapse_clause(loop)


def test_apply_loop_collapse_imperfect_default(parser, imperfection):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to an imperfect
    nest when the `collapse` keyword argument is not used.
    """
    schedule = get_schedule(
        parser, imperfectly_nested_triple_loop2[imperfection]
    )
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    apply_loop_collapse(loops[0])
    assert loops[0].parent.parent.collapse == 2
    assert has_collapse_clause(loops[0])
    assert has_collapse_clause(loops[1])
    assert not has_collapse_clause(loops[2])


def test_apply_loop_collapse_imperfect_default_error(parser, imperfection):
    """
    Test calling that :func:`apply_loop_collapse` without a `collapse` keyword
    argument raises an error when applied to an imperfect nest for which the
    outer loop is not itself in a perfect nest.
    """
    schedule = get_schedule(
        parser, imperfectly_nested_triple_loop1[imperfection]
    )
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    expected = "Expected an integer greater than one, not 1."
    with pytest.raises(ValueError, match=expected):
        apply_loop_collapse(loops[0])
