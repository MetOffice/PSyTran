# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

r"""
This module implements functions for querying whether :py:class:`Node`\s have
OpenACC clauses associated with them, as well as for applying such clauses.
"""

from psyacc.directives import (
    has_loop_directive,
    _check_directive,
)
from psyacc.family import get_ancestors
from psyacc.loop import _check_loop

__all__ = [
    "has_seq_clause",
    "has_gang_clause",
    "has_vector_clause",
    "has_collapse_clause",
]


def _prepare_loop_for_clause(loop, directive):
    """
    Prepare to apply a clause to a ``loop`` directive.

    :arg loop:       the Loop Node to prepare.
    :type loop:      :py:class:`Loop`
    :arg directive:  the directive to be applied
    :type directive: :py:class:`Directive`

    """
    _check_loop(loop)
    _check_directive(directive)


def has_seq_clause(loop):
    """
    Determine whether a loop has a ``seq`` clause.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop has a ``seq`` clause, else ``False``.
    :rtype: :py:class:`bool`
    """
    return has_loop_directive(loop) and loop.parent.parent.sequential


def has_gang_clause(loop):
    """
    Determine whether a loop has a ``gang`` clause.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop has a ``gang`` clause, else ``False``.
    :rtype: :py:class:`bool`
    """
    return has_loop_directive(loop) and loop.parent.parent.gang


def has_vector_clause(loop):
    """
    Determine whether a loop has a ``vector`` clause.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop has a ``vector`` clause, else ``False``.
    :rtype: :py:class:`bool`
    """
    return has_loop_directive(loop) and loop.parent.parent.vector


def has_collapse_clause(loop):
    """
    Determine whether a loop lies within a collapsed loop nest.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop has a ``collapse`` clause, else ``False``.
    :rtype: :py:class:`bool`
    """
    _check_loop(loop)
    # if not has_acc_kernels_directive(loop):
    #     return False
    ancestors = get_ancestors(loop, inclusive=True)
    for i, current in enumerate(ancestors):
        if has_loop_directive(current):
            print("got here")
            loop_dir = current.parent.parent
            collapse = loop_dir.collapse
            if collapse is None:
                continue
            return collapse > i
    return False
