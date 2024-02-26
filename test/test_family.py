# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from utils import *
import pytest


@pytest.fixture(params=[True, False])
def inclusive(request):
    return request.param


@pytest.fixture(params=[1, 2, 3, 4])
def nest_depth(request):
    return request.param


@pytest.fixture(params=["descendent", "ancestor"])
def relative(request):
    return request.param


get_relative = {
    "descendent": get_descendents,
    "ancestor": get_ancestors,
}


def test_get_relatives_typeerror1(parser, relative):
    """
    Test that a :class:`TypeError` is raised when :func:`get_descendents`
    or :func:`get_ancestors` is called with a non-Boolean ``inclusive`` flag.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected a bool, not '<class 'int'>'."
    with pytest.raises(AssertionError, match=expected):
        get_relative[relative](loops[0], inclusive=0)


def test_get_relatives_typeerror2(parser, relative):
    """
    Test that a :class:`TypeError` is raised when :func:`get_descendents`
    or :func:`get_ancestors` is called with a non-integer ``depth`` keyword
    argument.
    """
    schedule = get_schedule(parser, cs.double_loop_with_1_assignment)
    loops = schedule.walk(nodes.Loop)
    expected = "Expected an int, not '<class 'float'>'."
    with pytest.raises(AssertionError, match=expected):
        get_relative[relative](loops[0], depth=2.0)


def test_get_descendents_loop(parser, nest_depth, inclusive):
    """
    Test that :func:`get_descendents` correctly finds the right number of
    descendents of a loop.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    for i in range(nest_depth):
        loop = loops[i]
        kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
        expected = nest_depth - i if inclusive else nest_depth - 1 - i
        assert len(get_descendents(loop, **kwargs)) == expected
        kwargs["exclude"] = nodes.Loop
        assert len(get_descendents(loop, **kwargs)) == 0


def test_get_ancestors_loop(parser, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors of a loop.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loops = schedule.walk(nodes.Loop)
    for i in range(nest_depth):
        loop = loops[nest_depth - 1 - i]
        kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
        expected = nest_depth - i if inclusive else nest_depth - 1 - i
        assert len(get_ancestors(loop, **kwargs)) == expected
        kwargs["exclude"] = nodes.Loop
        assert len(get_ancestors(loop, **kwargs)) == 0


def test_get_descendents_loop_depth(parser, nest_depth, inclusive):
    """
    Test that :func:`get_descendents` correctly finds the right number of
    descendents of a loop of a specified depth.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loop = schedule.walk(nodes.Loop)[0]
    depth = loop.depth
    for i in range(nest_depth):
        kwargs = {
            "inclusive": inclusive,
            "node_type": nodes.Loop,
            "depth": depth,
        }
        num_descendents = len(get_descendents(loop, **kwargs))
        assert num_descendents == (0 if not inclusive and i == 0 else 1)
        depth += 2


def test_get_ancestors_loop_depth(parser, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors of a loop of a specified depth.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    loop = schedule.walk(nodes.Loop)[nest_depth - 1]
    depth = loop.depth
    for i in range(nest_depth):
        kwargs = {
            "inclusive": inclusive,
            "node_type": nodes.Loop,
            "depth": depth,
        }
        num_ancestors = len(get_ancestors(loop, **kwargs))
        assert num_ancestors == (0 if not inclusive and i == 0 else 1)
        depth -= 2


def test_get_descendents_assignment(parser, nest_depth, inclusive):
    """
    Test that :func:`get_descendents` correctly finds the right number of
    descendents of an assignment.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    assignment = schedule.walk(nodes.Assignment)[0]
    kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
    assert len(get_descendents(assignment, **kwargs)) == 0
    kwargs["exclude"] = nodes.Node
    assert len(get_descendents(assignment, **kwargs)) == 0


def test_get_ancestors_assignment(parser, nest_depth, inclusive):
    """
    Test that :func:`get_ancestors` correctly finds the right number of
    ancestors of an assignment.
    """
    schedule = get_schedule(parser, simple_loop_code(nest_depth))
    assignment = schedule.walk(nodes.Assignment)[0]
    kwargs = {"inclusive": inclusive, "node_type": nodes.Loop}
    assert len(get_ancestors(assignment, **kwargs)) == nest_depth
    kwargs["exclude"] = nodes.Loop
    assert len(get_ancestors(assignment, **kwargs)) == 0


def test_get_children(parser):
    """
    Test that :func:`get_children` correctly determines a node's children.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loop = schedule.walk(nodes.Loop)[0]
    assignments = schedule.walk(nodes.Assignment)
    assert get_children(loop) == assignments
    assert get_children(loop, node_type=nodes.Loop) == []
    assert get_children(loop, exclude=nodes.Assignment) == []


def test_get_parent(parser):
    """
    Test that :func:`get_parent` correctly determines a node's parent.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loop = schedule.walk(nodes.Loop)[0]
    for assignment in schedule.walk(nodes.Assignment):
        assert get_parent(assignment) == loop


def test_get_siblings(parser, inclusive):
    """
    Test that :func:`get_siblings` correctly determines a node's siblings.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    for i in range(3):
        kwargs = {"inclusive": inclusive}
        expected = list(assignments)
        if not inclusive:
            expected.pop(i)
        assert get_siblings(assignments[i], **kwargs) == expected
        kwargs["exclude"] = nodes.Assignment
        assert get_siblings(assignments[i], **kwargs) == []
        kwargs["node_type"] = nodes.Assignment
        assert get_siblings(assignments[i], **kwargs) == []


def test_has_ancestor_descendent(parser):
    """
    Test that :func:`has_ancestor` and :func:`has_descendent` correctly
    determine whether nodes have ancestors or descendents of specified types.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    loop = schedule.walk(nodes.Loop)[0]
    assignment = schedule.walk(nodes.Assignment)[0]
    assert has_descendent(loop, nodes.Assignment)
    assert not has_descendent(loop, nodes.Loop)
    assert has_ancestor(assignment, nodes.Loop)
    assert not has_ancestor(assignment, nodes.Assignment)


def test_has_ancestor_name(parser):
    """
    Test that :func:`has_ancestor` correctly determine whether nodes have
    ancestors whose variables have particular names.
    """
    schedule = get_schedule(parser, cs.loop_with_1_assignment)
    assignment = schedule.walk(nodes.Assignment)[0]
    assert has_ancestor(assignment, nodes.Loop, name="i")
    assert not has_ancestor(assignment, nodes.Loop, name="j")


def test_are_siblings(parser):
    """
    Test that :func:`are_siblings` correctly determines whether nodes are
    siblings.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    loop = schedule.walk(nodes.Loop)[0]
    assignments = schedule.walk(nodes.Assignment)
    assert are_siblings(*assignments[1:])
    assert are_siblings(*assignments)
    assert not are_siblings(assignments[0], loop)


def test_is_next_sibling(parser):
    """
    Test that :func:`is_next_sibling` correctly determines whether one node
    follows another.
    """
    schedule = get_schedule(parser, cs.loop_with_3_assignments)
    assignments = schedule.walk(nodes.Assignment)
    assert is_next_sibling(*assignments[:2])
    assert is_next_sibling(*assignments[1:])
    assert not is_next_sibling(*assignments[::2])
