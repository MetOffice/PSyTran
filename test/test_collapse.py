from psyclone.psyir import nodes
from psyacc.kernels import apply_kernels_directive
from psyacc.loop import apply_loop_directive
from psyacc.collapse import get_ancestors, apply_loop_collapse, is_collapsed
import code_snippets as cs
from utils import get_schedule, simple_loop_code
import pytest


@pytest.fixture(params=[True, False])
def inclusive(request):
    return request.param


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=[2, 3])
def collapse(request):
    return request.param


def test_get_ancestors(parser, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    expected = nest_depth if inclusive else nest_depth - 1
    assert len(get_ancestors(loops[-1], inclusive=inclusive)) == expected


def test_get_ancestors_typeerror1(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`get_ancestors`
    is called with something other than a :class:`Loop`.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    assignments = schedule.walk(nodes.Assignment)
    expected = (
        "Expected a Loop, not"
        " '<class 'psyclone.psyir.nodes.assignment.Assignment'>'."
    )
    with pytest.raises(TypeError, match=expected):
        get_ancestors(assignments[0])


def test_get_ancestors_typeerror2(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`get_ancestors`
    is called with a non-Boolean ``inclusive`` flag.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a bool, not '<class 'int'>'."
    with pytest.raises(TypeError, match=expected):
        get_ancestors(loops[0], inclusive=0)


def test_is_collapsed_no_kernels(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop which doesn't
    have a kernels directive.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    assert not is_collapsed(loops[0])


def test_is_collapsed_kernels_no_loop(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop with a kernels
    directive but no loop directives.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    assert not is_collapsed(loops[0])


def test_is_collapsed_loop_no_collapse(parser):
    """
    Test that :func:`is_collapsed` returns ``False`` for a loop with a loop
    directive but no collapse clause.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    apply_kernels_directive(loops[0])
    apply_loop_directive(loops[0])
    assert not is_collapsed(loops[0])


def test_apply_loop_collapse_typeerror(parser):
    """
    Test that a :class:`TypeError` is raised when :func:`apply_loop_directive`
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
    Test that a :class:`ValueError` is raised when :func:`apply_loop_directive`
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
    Test that a :class:`ValueError` is raised when :func:`apply_loop_directive`
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
        assert is_collapsed(loop)


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
        assert is_collapsed(loops[i])
    assert loops[-1].parent.parent.collapse is None
    assert not is_collapsed(loops[-1])
