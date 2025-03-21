# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for PSyTran's `directives` module.
"""

import pytest

from psyclone.psyir import nodes
from psyclone.psyir.nodes import (
    OMPDoDirective,
    OMPLoopDirective,
    OMPParallelDoDirective,
    OMPTeamsDistributeParallelDoDirective,
    OMPTeamsLoopDirective,
)
from psyclone.psyir.transformations import ACCKernelsTrans
from psyclone.transformations import (
    ACCKernelsDirective,
    ACCLoopDirective,
    ACCLoopTrans,
    OMPLoopTrans,
)
from utils import get_schedule, has_clause

import code_snippets as cs
from psytran.clauses import has_gang_clause, has_seq_clause, has_vector_clause
from psytran.directives import (
    apply_parallel_directive,
    apply_loop_directive,
    has_parallel_directive,
    has_loop_directive,
    _check_directive,
)


def test_apply_directive_typeerror(fortran_reader, trans_directive):
    """
    Test that a :class:`TypeError` is raised when an attempt is made to apply
    directives with options that aren't a :class:`dict`.
    """
    trans, _ = trans_directive
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a dict, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        apply_parallel_directive(loops[0], trans, options=0)


def test_apply_directive_schedule(fortran_reader, trans_directive):
    """
    Test that directives can be correctly applied to a schedule.
    """
    trans, directive = trans_directive
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    apply_parallel_directive(schedule, trans)
    assert isinstance(schedule[0], directive)


def test_apply_directive_schedule_with_intrinsic_call(
    fortran_reader, trans_directive
):
    """
    Test that directives may be correctly applied to a schedule containing a
    loop with an intrinsic call.
    """
    trans, directive = trans_directive
    schedule = get_schedule(
        fortran_reader, cs.loop_with_1_assignment_and_intrinsic_call
    )
    apply_parallel_directive(schedule, trans)
    assert isinstance(schedule[0], directive)


def test_apply_directive_loop(fortran_reader, trans_directive):
    """
    Test directives may be correctly applied to a loop.
    """
    trans, directive = trans_directive
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_parallel_directive(loops[0], trans)
    assert isinstance(loops[0].parent.parent, directive)
    assert has_parallel_directive(loops[0], directive)
    assert has_parallel_directive(loops, directive)


def test_check_directive(loop_trans, omp_directive):
    """
    Test that `_check_directive` correctly identifies allowed loop directives.
    """
    # Check that all types of OMP loop directives are allowed
    if isinstance(loop_trans, OMPLoopTrans):
        loop_trans = OMPLoopTrans(omp_directive=omp_directive)
    _check_directive(loop_trans)


def test_check_directive_unsupported(loop_trans=None):
    """
    Test that `_check_directive` correctly raises and error when an unsupported
    loop directive is passed.
    """
    # Not supported
    expected = (
        "Supplied directive type is not a supported loop directive, "
        "found <class 'NoneType'>"
    )
    with pytest.raises(ValueError, match=expected):
        _check_directive(loop_trans)


def test_has_no_directive(fortran_reader, trans_directive):
    """
    Test a lack of directives can be correctly identified.
    """
    _, directive = trans_directive
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_parallel_directive(loops[0], directive)


def test_has_no_directive_block(fortran_reader, trans_directive):
    """
    Test a lack of directives can be correctly identified when applied to a
    block of code.
    """
    _, directive = trans_directive
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_parallel_directive(loops, directive)


def test_force_apply_loop_directive(fortran_reader, loop_trans, omp_directive):
    """
    Test that :func:`apply_loop_directive` correctly force-applies a ``loop``
    directive.
    """
    schedule = get_schedule(fortran_reader, cs.serial_loop)
    loops = schedule.walk(nodes.Loop)
    if isinstance(loop_trans, ACCLoopTrans):
        apply_parallel_directive(loops[0], ACCKernelsTrans)
        apply_loop_directive(loops[0], loop_trans, options={"force": True})
        assert isinstance(loops[0].parent.parent, ACCLoopDirective)
    # For OMP there are several directives that can be passed to OMPLoop
    elif isinstance(loop_trans, OMPLoopTrans):
        loop_trans = OMPLoopTrans(omp_directive=omp_directive)
        apply_loop_directive(loops[0], loop_trans, options={"force": True})
        match omp_directive:
            case "do":
                assert isinstance(loops[0].parent.parent, OMPDoDirective)
            case "loop":
                assert isinstance(loops[0].parent.parent, OMPLoopDirective)
            case "paralleldo":
                assert isinstance(
                    loops[0].parent.parent, OMPParallelDoDirective
                )
            case "teamsdistributeparalleldo":
                assert isinstance(
                    loops[0].parent.parent,
                    OMPTeamsDistributeParallelDoDirective,
                )
            case "teamsloop":
                assert isinstance(
                    loops[0].parent.parent, OMPTeamsLoopDirective
                )


def test_force_apply_loop_directive_with_seq_clause(
    fortran_reader, trans_directive, loop_trans=ACCLoopTrans()
):
    """
    Test that :func:`apply_loop_directive` correctly force-applies a ``loop``
    directive with a ``seq`` clause for loops.
    """
    trans, directive = trans_directive
    schedule = get_schedule(fortran_reader, cs.serial_loop)
    loops = schedule.walk(nodes.Loop)
    apply_parallel_directive(loops[0], trans)
    if isinstance(directive, ACCKernelsDirective):
        apply_loop_directive(
            loops[0], loop_trans, options={"force": True, "sequential": True}
        )
        assert isinstance(loops[0].parent.parent, ACCLoopDirective)
        assert has_seq_clause(loops[0])


def test_apply_loop_directive_with_clause(
    fortran_reader, trans_directive, clause, loop_trans=ACCLoopTrans()
):
    """
    Test that :func:`apply_loop_directive` correctly applies a ``loop``
    directive with a clause.
    """
    trans, directive = trans_directive
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_parallel_directive(loops[0], trans)
    if isinstance(directive, ACCKernelsDirective):
        apply_loop_directive(loops[0], loop_trans, options={clause: True})
        assert isinstance(loops[0].parent.parent, ACCLoopDirective)
        assert has_clause[clause](loops[0])


def test_apply_loop_directive_with_gang_vector(
    fortran_reader, trans_directive, loop_trans=ACCLoopTrans()
):
    """
    Test that :func:`apply_loop_directive` correctly applies a ``loop``
    directive with ``gang`` and ``vector`` clauses.
    """
    trans, directive = trans_directive
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_parallel_directive(loops[0], trans)
    if isinstance(directive, ACCKernelsDirective):
        apply_loop_directive(
            loops[0], loop_trans, options={"gang": True, "vector": True}
        )
        assert isinstance(loops[0].parent.parent, ACCLoopDirective)
        assert has_gang_clause(loops[0])
        assert has_vector_clause(loops[0])


def test_apply_loop_directive_typeerror1(fortran_reader, loop_trans):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
    is called with something other than a :class:`Loop`.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    assignments = schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        apply_loop_directive(assignments[0], loop_trans)


def test_apply_loop_directive_typeerror2(fortran_reader, loop_trans):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
    is called with options that aren't a :class:`dict`.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a dict, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        apply_loop_directive(loops[0], loop_trans, options=0)


def test_apply_loop_directive_valueerror(fortran_reader, loop_trans):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_directive`
    is called to apply an ACC loop directive with no ``kernels`` directive
    present OR is called to apply an OMP loop directive when a ``kernels``
    directive is present.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    if isinstance(loop_trans, ACCLoopTrans):
        expected = (
            "Cannot apply an ACC loop directive without a "
            "kernels directive."
        )
        with pytest.raises(ValueError, match=expected):
            apply_loop_directive(loops[0], loop_trans)
    if isinstance(loop_trans, OMPLoopTrans):
        apply_parallel_directive(loops[0], ACCKernelsTrans)
        expected = (
            "Cannot apply an OMP loop directive to a kernel with an "
            "ACC kernels directive."
        )
        with pytest.raises(ValueError, match=expected):
            apply_loop_directive(loops[0], loop_trans)


def test_has_no_loop_directive(fortran_reader):
    """
    Test that :func:`has_loop_directive` correctly identifies no ``loop``
    directives.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_loop_directive(loops[0])
