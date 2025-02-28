# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for PSyACC's `clauses` module.
"""

import pytest

import code_snippets as cs
from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopDirective
from utils import get_schedule, has_clause, simple_loop_code

from psyacc.clauses import _prepare_loop_for_clause, has_collapse_clause
from psyacc.directives import apply_loop_directive, apply_acc_kernels_directive


imperfectly_nested_triple_loop1 = {
    "before": cs.imperfectly_nested_triple_loop1_before,
    "after": cs.imperfectly_nested_triple_loop1_after,
}

imperfectly_nested_triple_loop2 = {
    "before": cs.imperfectly_nested_triple_loop2_before,
    "after": cs.imperfectly_nested_triple_loop2_after,
}


def test_prepare_loop_for_clause_no_kernels_error(fortran_reader):
    """
    Test that a :class:`ValueError` is raised when
    :func:`_prepare_loop_for_clause` is called without a kernels directive.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Cannot apply a loop clause without a kernels directive."
    with pytest.raises(ValueError, match=expected):
        _prepare_loop_for_clause(loops[0])


def test_prepare_loop_for_clause_no_loop_dir(fortran_reader):
    """
    Test that :func:`_prepare_loop_for_clause` is correctly applied when there
    is no loop directive.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    _prepare_loop_for_clause(loops[0])
    assert isinstance(loops[0].parent.parent, ACCLoopDirective)


def test_no_loop_clause(fortran_reader, nest_depth, clause):
    """
    Test that a lack of each clause is correctly identified.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    for i in range(nest_depth):
        assert not has_clause[clause](loops[i])


def test_has_collapse_clause_no_kernels(fortran_reader):
    """
    Test that :func:`has_collapse_clause` returns ``False`` for a loop with no
    ``kernels`` directive.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_collapse_clause(loops[0])


def test_has_collapse_clause_kernels_no_loop(fortran_reader):
    """
    Test that :func:`has_collapse_clause` returns ``False`` for a loop with a
    ``kernels`` directive but no ``loop`` directives.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    assert not has_collapse_clause(loops[0])


def test_has_collapse_clause_loop_no_collapse(fortran_reader):
    """
    Test that :func:`has_collapse_clause` returns ``False`` for a loop with a
    ``loop`` directive but no ``collapse`` clause.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    assert not has_collapse_clause(loops[0])


def test_apply_loop_collapse(fortran_reader, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a full nest.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(collapse))
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    apply_loop_directive(loops[0], options={"collapse": collapse})
    assert loops[0].parent.parent.collapse == collapse
    for loop in loops:
        assert has_collapse_clause(loop)


def test_apply_loop_collapse_subnest(fortran_reader, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a sub-nest.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(collapse + 1))
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    apply_loop_directive(loops[-1])
    apply_loop_directive(loops[0], options={"collapse": collapse})
    assert loops[0].parent.parent.collapse == collapse
    for i in range(collapse):
        assert has_collapse_clause(loops[i])
    assert loops[-1].parent.parent.collapse is None
    assert not has_collapse_clause(loops[-1])


def test_apply_loop_collapse_default(fortran_reader, collapse):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a full nest
    when the `collapse` keyword argument is not used.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(collapse))
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    apply_loop_directive(loops[0], options={"collapse": collapse})
    assert loops[0].parent.parent.collapse == collapse
    for loop in loops:
        assert has_collapse_clause(loop)


def test_apply_loop_collapse_imperfect_default(
    fortran_reader, imperfection, collapse
):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to an imperfect
    nest when the `collapse` keyword argument is not used.
    """
    if imperfection == "if":
        return

    schedule = get_schedule(
        fortran_reader, imperfectly_nested_triple_loop2[imperfection]
    )
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    apply_loop_directive(loops[0], options={"collapse": collapse})
    assert loops[0].parent.parent.collapse == 2
    assert has_collapse_clause(loops[0])
    assert has_collapse_clause(loops[1])
    assert not has_collapse_clause(loops[2])
