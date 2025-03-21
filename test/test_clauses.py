# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for PSyTran's `clauses` module.
"""

import pytest

import code_snippets as cs
from psyclone.psyir import nodes
from psyclone.transformations import ACCLoopTrans
from psyclone.psyir.transformations import ACCKernelsTrans
from utils import get_schedule, has_clause, simple_loop_code

from psytran.clauses import _prepare_loop_for_clause, has_collapse_clause
from psytran.directives import (
    apply_loop_directive,
    apply_parallel_directive,
)


imperfectly_nested_triple_loop1 = {
    "before": cs.imperfectly_nested_triple_loop1_before,
    "after": cs.imperfectly_nested_triple_loop1_after,
}

imperfectly_nested_triple_loop2 = {
    "before": cs.imperfectly_nested_triple_loop2_before,
    "after": cs.imperfectly_nested_triple_loop2_after,
}


def test_prepare_loop_for_clause_no_loop_dir(fortran_reader, loop_trans=None):
    """
    Test that :func:`_prepare_loop_for_clause` raises an error when there
    is no loop directive.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = (
        "Supplied directive type is not a supported loop directive, "
        "found <class 'NoneType'>"
    )
    with pytest.raises(ValueError, match=expected):
        _prepare_loop_for_clause(loops[0], loop_trans)


def test_no_loop_clause(fortran_reader, nest_depth, clause):
    """
    Test that a lack of each clause is correctly identified.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    apply_parallel_directive(loops[0], ACCKernelsTrans)
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
    apply_parallel_directive(loops[0], ACCKernelsTrans)
    assert not has_collapse_clause(loops[0])


def test_has_collapse_clause_loop_no_collapse(fortran_reader, loop_trans):
    """
    Test that :func:`has_collapse_clause` returns ``False`` for a loop with a
    ``loop`` directive but no ``collapse`` clause.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    if isinstance(loop_trans, ACCLoopTrans):
        apply_parallel_directive(loops[0], ACCKernelsTrans)
    apply_loop_directive(loops[0], loop_trans)
    assert not has_collapse_clause(loops[0])


def test_apply_loop_collapse(fortran_reader, collapse, loop_trans):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a full nest.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(collapse))
    loops = schedule.walk(nodes.Loop)
    if isinstance(loop_trans, ACCLoopTrans):
        apply_parallel_directive(loops[0], ACCKernelsTrans)
    apply_loop_directive(loops[0], loop_trans, options={"collapse": collapse})
    assert loops[0].parent.parent.collapse == collapse
    for loop in loops:
        assert has_collapse_clause(loop)


def test_apply_loop_collapse_subnest(fortran_reader, collapse, loop_trans):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a sub-nest.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(collapse + 1))
    loops = schedule.walk(nodes.Loop)
    if isinstance(loop_trans, ACCLoopTrans):
        apply_parallel_directive(loops[0], ACCKernelsTrans)
    apply_loop_directive(loops[0], loop_trans)
    apply_loop_directive(loops[-1], loop_trans)
    apply_loop_directive(loops[0], loop_trans, options={"collapse": collapse})
    assert loops[0].parent.parent.collapse == collapse
    for i in range(collapse):
        assert has_collapse_clause(loops[i])
    assert loops[-1].parent.parent.collapse is None
    assert not has_collapse_clause(loops[-1])


def test_apply_loop_collapse_default(fortran_reader, collapse, loop_trans):
    """
    Test that :func:`apply_loop_collapse` is correctly applied to a full nest
    when the `collapse` keyword argument is not used.
    """
    schedule = get_schedule(fortran_reader, simple_loop_code(collapse))
    loops = schedule.walk(nodes.Loop)
    if isinstance(loop_trans, ACCLoopTrans):
        apply_parallel_directive(loops[0], ACCKernelsTrans)
    apply_loop_directive(loops[0], loop_trans, options={"collapse": collapse})
    assert loops[0].parent.parent.collapse == collapse
    for loop in loops:
        assert has_collapse_clause(loop)


def test_apply_loop_collapse_imperfect_default(
    fortran_reader, imperfection, collapse, loop_trans
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
    if isinstance(loop_trans, ACCLoopTrans):
        apply_parallel_directive(loops[0], ACCKernelsTrans)
    apply_loop_directive(loops[0], loop_trans, options={"collapse": collapse})
    assert loops[0].parent.parent.collapse == 2
    assert has_collapse_clause(loops[0])
    assert has_collapse_clause(loops[1])
    assert not has_collapse_clause(loops[2])
