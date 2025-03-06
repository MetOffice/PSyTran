# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Unit tests for PSyACC's `directives` module.
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
from psyclone.transformations import (
    ACCKernelsDirective,
    ACCLoopDirective,
    ACCLoopTrans,
    OMPLoopTrans,
)
from utils import get_schedule, has_clause

import code_snippets as cs
from psyacc.clauses import has_gang_clause, has_seq_clause, has_vector_clause
from psyacc.directives import (
    apply_acc_kernels_directive,
    apply_loop_directive,
    has_acc_kernels_directive,
    has_loop_directive,
    _check_directive,
)


def test_apply_acc_kernels_directive_typeerror(fortran_reader):
    """
    Test that a :class:`TypeError` is raised when
    :func:`apply_acc_kernels_directive` is called with options that aren't a
    :class:`dict`.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a dict, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        apply_acc_kernels_directive(loops[0], options=0)


def test_apply_acc_kernels_directive_schedule(fortran_reader):
    """
    Test that :func:`apply_acc_kernels_directive` correctly applies a ``kernels``
    directive to a schedule.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    apply_acc_kernels_directive(schedule)
    assert isinstance(schedule[0], ACCKernelsDirective)


def test_apply_acc_kernels_directive_schedule_with_intrinsic_call(
    fortran_reader,
):
    """
    Test that :func:`apply_acc_kernels_directive` correctly applies a ``kernels``
    directive to a schedule containing a loop with an intrinsic call.
    """
    schedule = get_schedule(
        fortran_reader, cs.loop_with_1_assignment_and_intrinsic_call
    )
    apply_acc_kernels_directive(schedule)
    assert isinstance(schedule[0], ACCKernelsDirective)


def test_apply_acc_kernels_directive_loop(fortran_reader):
    """
    Test that :func:`apply_acc_kernels_directive` correctly applies a ``kernels``
    directives to a loop.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_acc_kernels_directive(loops[0])
    assert isinstance(loops[0].parent.parent, ACCKernelsDirective)
    assert has_acc_kernels_directive(loops[0])
    assert has_acc_kernels_directive(loops)


def test_check_directive(directive, omp_directive):
    """
    Test that `_check_directive` correctly identifies allowed loop directives.
    """
    # Check that all types of OMP loop directives are allowed
    if isinstance(directive, OMPLoopTrans):
        directive = OMPLoopTrans(omp_directive=omp_directive)
        print(type(directive))
        _check_directive(directive)
    # ACC directive allowed
    _check_directive(directive)


def test_check_directive_unsupported(directive=None):
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
        _check_directive(directive)


def test_has_no_kernels_directive(fortran_reader):
    """
    Test that :func:`has_acc_kernels_directive` correctly identifies no OpenACC
    kernels directives.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_acc_kernels_directive(loops[0])


def test_has_no_kernels_directive_block(fortran_reader):
    """
    Test that :func:`has_acc_kernels_directive` correctly identifies no OpenACC
    kernels directives when applied to a block of code.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_acc_kernels_directive(loops)


def test_force_apply_loop_directive(fortran_reader, directive, omp_directive):
    """
    Test that :func:`apply_loop_directive` correctly force-applies a ``loop``
    directive.
    """
    schedule = get_schedule(fortran_reader, cs.serial_loop)
    loops = schedule.walk(nodes.Loop)
    if isinstance(directive, ACCLoopTrans):
        apply_acc_kernels_directive(loops[0])
        apply_loop_directive(loops[0], directive, options={"force": True})
        assert isinstance(loops[0].parent.parent, ACCLoopDirective)
    # For OMP there are several directives that can be passed to OMPLoop
    elif isinstance(directive, OMPLoopTrans):
        directive = OMPLoopTrans(omp_directive=omp_directive)
        apply_loop_directive(loops[0], directive, options={"force": True})
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


def test_force_apply_loop_directive_with_seq_clause(fortran_reader, directive):
    """
    Test that :func:`apply_loop_directive` correctly force-applies a ``loop``
    directive with a ``seq`` clause for loops.
    """
    schedule = get_schedule(fortran_reader, cs.serial_loop)
    loops = schedule.walk(nodes.Loop)
    if isinstance(directive, ACCLoopTrans):
        apply_acc_kernels_directive(loops[0])
        apply_loop_directive(
            loops[0], directive, options={"force": True, "sequential": True}
        )
        assert isinstance(loops[0].parent.parent, ACCLoopDirective)
        assert has_seq_clause(loops[0])


def test_apply_loop_directive_with_clause(fortran_reader, clause, directive):
    """
    Test that :func:`apply_loop_directive` correctly applies a ``loop``
    directive with a clause.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    if isinstance(directive, ACCLoopTrans):
        apply_acc_kernels_directive(loops[0])
        apply_loop_directive(loops[0], directive, options={clause: True})
        assert isinstance(loops[0].parent.parent, ACCLoopDirective)
        assert has_clause[clause](loops[0])


def test_apply_loop_directive_with_gang_vector(fortran_reader, directive):
    """
    Test that :func:`apply_loop_directive` correctly applies a ``loop``
    directive with ``gang`` and ``vector`` clauses.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    if isinstance(directive, ACCLoopTrans):
        apply_acc_kernels_directive(loops[0])
        apply_loop_directive(
            loops[0], directive, options={"gang": True, "vector": True}
        )
        assert isinstance(loops[0].parent.parent, ACCLoopDirective)
        assert has_gang_clause(loops[0])
        assert has_vector_clause(loops[0])


def test_apply_loop_directive_typeerror1(fortran_reader, directive):
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
        apply_loop_directive(assignments[0], directive)


def test_apply_loop_directive_typeerror2(fortran_reader, directive):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
    is called with options that aren't a :class:`dict`.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a dict, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        apply_loop_directive(loops[0], directive, options=0)


def test_apply_loop_directive_valueerror(fortran_reader, directive):
    """
    Test that a :class:`ValueError` is raised when :func:`apply_loop_directive`
    is called to a loop with no ``kernels`` directive.
    """
    schedule = get_schedule(fortran_reader, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    if isinstance(directive, ACCLoopTrans):
        expected = (
            "Cannot apply an ACC loop directive without a "
            "kernels directive."
        )
        with pytest.raises(ValueError, match=expected):
            apply_loop_directive(loops[0], directive)
    if isinstance(directive, OMPLoopTrans):
        apply_acc_kernels_directive(loops[0])
        expected = (
            "Cannot apply an OMP loop directive to a kernel with an "
            "ACC kernels directive."
        )
        with pytest.raises(ValueError, match=expected):
            apply_loop_directive(loops[0], directive)


def test_has_no_loop_directive(fortran_reader):
    """
    Test that :func:`has_loop_directive` correctly identifies no ``loop``
    directives.
    """
    schedule = get_schedule(fortran_reader, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not has_loop_directive(loops[0])
