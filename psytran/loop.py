# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

r"""
This module provides various utility functions for querying :py:class:`Loop`
Nodes, as well as for going between outer Loops and their associated Loop
nests.
"""

from collections.abc import Iterable
from psyclone.psyir import nodes
from psytran.family import get_children, get_descendents

__all__ = [
    "is_outer_loop",
    "loop2nest",
    "nest2loop",
    "is_perfectly_nested",
    "is_simple_loop",
    "is_independent",
    "is_parallelisable",
]


def _check_loop(node):
    """
    Check that we do indeed have a Loop Node.

    :arg node: the Node to check.
    :type node: :py:class:`Node`

    :raises TypeError: if the loop argument is not a Loop Node.
    """
    if not isinstance(node, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(node)}'.")


def is_outer_loop(loop):
    """
    Determine whether a Loop is outer-most in its nest.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop is outer-most, else ``False``.
    :rtype: :py:class:`bool`
    """
    _check_loop(loop)
    return loop.ancestor(nodes.Loop) is None


def loop2nest(loop):
    """
    Given a Loop, obtain all of its descendent loops (inclusive).

    :arg loop: the Loop Node to extract a nest from.
    :type loop: :py:class:`Loop`

    :returns: the Loop nest.
    :rtype: :py:class:`list`
    """
    _check_loop(loop)
    return get_descendents(loop, node_type=nodes.Loop, inclusive=True)


def nest2loop(loops):
    """
    Given a Loop nest, validate it and return its outer-most Loop.

    :arg loops: the nest to extract the outer-most Loop from.
    :type loops: :py:class:`list`

    :returns: the outer Loop.
    :rtype: :py:class:`Loop`
    """
    outer_loop = loops[0]
    descendents = loop2nest(outer_loop)
    for loop in loops:
        _check_loop(loop)
        assert loop in descendents
    return outer_loop


def is_perfectly_nested(outer_loop_or_subnest):
    r"""
    Determine whether a Loop (sub)nest is perfect, i.e., each level except the
    deepest contains only the next Loop.

    Note that we ignore nodes of type :class:`Literal` and :class:`Reference`.

    Note also that the 'outer loop' here is not necessarily the outer-most loop
    in the schedule, just the outer-most loop in the sub-nest.

    :arg outer_loop_or_subnest: either the outer loop of the subnest, or the
        subnest as a list of Loops
    :type outer_loop_or_subnest: :py:class:`list` or :py:class:`Loop`

    :returns: ``True`` if the Loop nest is perfect, else ``False``.
    :rtype: :py:class:`bool`
    """
    exclude = (
        nodes.literal.Literal,
        nodes.reference.Reference,
        nodes.Loop,
        nodes.IntrinsicCall,
    )

    # Switch for input type
    if isinstance(outer_loop_or_subnest, Iterable):
        subnest = outer_loop_or_subnest
        outer_loop = nest2loop(subnest)
    else:
        outer_loop = outer_loop_or_subnest
        subnest = loop2nest(outer_loop)

    def intersect(list1, list2):
        r"""
        Return the intersection of two lists. Note that we cannot use the
        in-built set intersection functionality because PSyclone
        :class:`Node`\s are not hashable.

        :arg list1: the first list
        :type list1: :py:class:`list`
        :arg list2: the second list
        :type list2: :py:class:`list`

        :returns: the intersection.
        :rtype: :py:class:`list`
        """
        return [item for item in list1 if item in list2]

    # Check whether the subnest is perfect by checking each level in turn
    loops, non_loops = [outer_loop], []
    while len(loops) > 0:
        non_loops = get_children(loops[0], exclude=exclude)
        loops = intersect(
            get_children(loops[0], node_type=nodes.Loop), subnest
        )

        # Case of one loop and no non-loops: this nest level is okay
        if len(loops) == 1 and not non_loops:
            continue

        # Case of no loops and no non-loops with descendents outside of the
        # subnest: this nest level is also okay
        if not loops:
            for node in non_loops:
                if intersect(node.walk(nodes.Loop), subnest):
                    break
            else:
                continue

        # Otherwise, the nest level is not okay
        return False
    return True


def is_simple_loop(loop):
    """
    Determine whether a Loop nest is simple, i.e., perfectly nested, with only
    literal assignments at the deepest level.

    :arg loop: the outer-most Loop of the nest
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop nest is simple, else ``False``.
    :rtype: :py:class:`bool`
    """
    return is_perfectly_nested(loop) and all(
        isinstance(child, nodes.Assignment) and child.walk(nodes.Literal)
        for child in get_children(loop2nest(loop)[-1])
    )


def is_independent(loop):
    """
    Determine whether a perfectly nested Loop is independent.

    :arg loop: the Loop to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop nest is independent, else ``False``.
    :rtype: :py:class:`bool`

    :raises ValueError: if the loop is not perfectly nested.
    """
    if not is_perfectly_nested(loop):
        raise ValueError(
            "is_independent can only be applied to perfectly nested loops."
        )
    previous_variables = []
    while isinstance(loop, nodes.Loop):
        previous_variables.append(loop.variable)
        loop = loop.loop_body.children[0]
        if not isinstance(loop, nodes.Loop):
            continue
        for bound in (loop.start_expr, loop.stop_expr, loop.step_expr):
            for ref in bound.walk(nodes.Reference):
                if ref.symbol in previous_variables:
                    return False
    return True


def is_parallelisable(loop):
    """
    Determine whether a Loop can be parallelised.

    Note: wraps the :meth:`independent_iterations` method of the Loop node.

    :arg loop: the Loop to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop nest is parallelisable, else ``False``.
    :rtype: :py:class:`bool`
    """
    return loop.independent_iterations()


def get_perfectly_nested_loops(schedule):
    """
    Finds the outermost of all perfectly nested loop structures within a
    supplied schedule and returns them as a list.

    Does NOT nexcessarily return an outer loop, only the topmost loop of a
    perfectly nested structure.

    :arg schedule: the schedule to search.
    :type schedule: :py:class:`Schedule`

    :returns loops: all loops that are the outermost of a perfectly nested
                    structure.
    :rtype loops: list[:py:class:`Loop`]
    """
    loops = []

    # Test all loops in schedule to see if they are perfectly nested
    for loop in schedule.walk(nodes.Loop):
        if is_perfectly_nested(loop):
            loops.append(loop)

    # For each loop in the list check if loops below it are a descendent and
    # remove them if they are
    for top_loop in loops[:]:
        for bottom_loop in reversed(loops[:]):
            if bottom_loop in get_descendents(top_loop):
                loops.remove(bottom_loop)

    # return list of perfectly nested loops
    return loops
