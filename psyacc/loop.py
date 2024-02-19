# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyclone.psyir.tools import DependencyTools
from psyacc.family import get_children, get_descendents
from collections.abc import Iterable

__all__ = [
    "is_outer_loop",
    "loop2nest",
    "nest2loop",
    "is_perfectly_nested",
    "is_simple_loop",
    "get_loop_variable_name",
    "get_loop_nest_variable_names",
    "is_independent",
    "is_parallelisable",
]


def _check_loop(loop):
    """
    Check that we do indeed have a :class:`psyclone.psyir.nodes.loop.Loop` node.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")


def is_outer_loop(loop):
    """
    Determine whether a loop is outer-most in its nest.
    """
    _check_loop(loop)
    return loop.ancestor(nodes.Loop) is None


def loop2nest(loop):
    """
    Given a loop, obtain all of its descendent loops (inclusive).

    :arg loop: the :class:`psyclone.psyir.nodes.loop.Loop`
    """
    _check_loop(loop)
    return get_descendents(loop, node_type=nodes.Loop, inclusive=True)


def nest2loop(loops):
    """
    Given a loop nest, validate it and return its outer-most loop.
    """
    outer_loop = loops[0]
    descendents = loop2nest(outer_loop)
    for loop in loops:
        _check_loop(loop)
        assert loop in descendents
    return outer_loop


def is_perfectly_nested(outer_loop_or_subnest):
    r"""
    Determine whether a loop (sub)nest is perfect, i.e., each level except the deepest
    contains only the next loop.

    Note that we ignore nodes of type :class:`psyclone.psyir.nodes.literal.Literal` and
    :class:`psyclone.psyir.nodes.reference.Reference`.

    Note also that the 'outer loop' here is not necessarily the outer-most loop in the
    schedule, just the outer-most loop in the sub-nest.

    :arg outer_loop_or_subnest: either the outer loop of the subnest, or the subnest as
        a list of :class:`psyclone.psyir.nodes.loop.Loop`\s
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
        Return the intersection of two lists. Note that we cannot use the in-built set
        intersection functionality because PSyclone
        :class:`psyclone.psyir.nodes.node.Node`\s are not hashable.
        """
        return [item for item in list1 if item in list2]

    # Check whether the subnest is perfect by checking each level in turn
    loops, non_loops = [outer_loop], []
    while len(loops) > 0:
        non_loops = get_children(loops[0], exclude=exclude)
        loops = intersect(get_children(loops[0], node_type=nodes.Loop), subnest)

        # Case of one loop and no non-loops: this nest level is okay
        if len(loops) == 1 and not non_loops:
            continue

        # Case of no loops and no non-loops with descendents outside of the subnest:
        # this nest level is also okay
        if not loops:
            for node in non_loops:
                if intersect(node.walk(nodes.Loop), subnest):
                    break
            else:
                continue

        # Otherwise, the nest level is not okay
        return False
    else:
        return True


def is_simple_loop(loop):
    """
    Determine whether a loop nest is simple, i.e., perfectly nested, with only
    literal assignments at the deepest level.

    :arg loop: the outer-most loop of the nest
    """
    return is_perfectly_nested(loop) and all(
        [
            isinstance(child, nodes.Assignment) and child.walk(nodes.Literal)
            for child in get_children(loop2nest(loop)[-1])
        ]
    )


def get_loop_variable_name(loop):
    """
    Given a :class:`psyclone.psyir.nodes.loop.Loop` node, return its variable name.
    """
    assert isinstance(loop, nodes.Loop)
    return loop.variable.name


def get_loop_nest_variable_names(loop):
    """
    Given a :class:`psyclone.psyir.nodes.loop.Loop` node, return the variable names of
    each loop it contains.
    """
    assert isinstance(loop, nodes.Loop)
    return [get_loop_variable_name(loop) for loop in loop2nest(loop)]


def is_independent(loop):
    """
    Determine whether a perfectly nested :class:`psyclone.psyir.nodes.loop.Loop` is
    independent.
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
    else:
        return True


def is_parallelisable(loop):
    """
    Determine whether a :class:`psyclone.psyir.nodes.loop.Loop` can be parallelised.

    Note: wraps the :meth:`can_loop_be_parallelised` method of
    :class:`psyclone.psyir.tools.dependency_tools.DependencyTools`.
    """
    return DependencyTools().can_loop_be_parallelised(loop)
