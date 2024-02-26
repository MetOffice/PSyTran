# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyclone.transformations import (
    ACCKernelsDirective,
    ACCKernelsTrans,
    ACCLoopDirective,
    ACCLoopTrans,
)
from collections.abc import Iterable
from psyacc.family import get_parent
from psyacc.loop import _check_loop

__all__ = [
    "apply_kernels_directive",
    "has_kernels_directive",
    "apply_loop_directive",
    "has_loop_directive",
]


def apply_kernels_directive(block, options={}):
    """
    Apply a ``kernels`` directive to a block of code.

    :arg block: the block of code to apply the directive to.
    :type block: :py:class:`list`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`

    :raises TypeError: if the options argument is not a dictionary.
    """
    if not isinstance(options, dict):
        raise TypeError(f"Expected a dict, not '{type(options)}'.")
    ACCKernelsTrans().apply(block, options=options)


def has_kernels_directive(node):
    """
    Determine whether a node is inside a ``kernels`` directive.

    :arg node: the Node to check.
    :type node: :py:class:`Node`

    :returns: ``True`` if the Node has a ``kernels`` directive, else ``False``.
    :rtype: :py:class:`bool`
    """
    if isinstance(node, Iterable):
        return has_kernels_directive(node[0])
    assert isinstance(node, nodes.Node)
    return bool(node.ancestor(ACCKernelsDirective))


def apply_loop_directive(loop, options={}):
    """
    Apply a ``loop`` directive.

    :arg loop: the Loop Node to apply the directive to.
    :type loop: :py:class:`Loop`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`

    :raises TypeError: if the options argument is not a dictionary.
    :raises ValueError: if a ``kernels`` directive has not yet been applied.
    """
    _check_loop(loop)
    if not isinstance(options, dict):
        raise TypeError(f"Expected a dict, not '{type(options)}'.")
    if not has_kernels_directive(loop):
        raise ValueError(
            "Cannot apply a loop directive without a kernels directive."
        )
    ACCLoopTrans().apply(loop, options=options)


def has_loop_directive(loop):
    """
    Determine whether a node has an OpenACC ``loop`` directive.

    :arg loop: the Loop Node to check.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Node has a ``loop`` directive, else ``False``.
    :rtype: :py:class:`bool`
    """
    assert isinstance(loop, nodes.Loop)
    parent = get_parent(loop)
    return isinstance(parent, ACCLoopDirective) and has_kernels_directive(loop)
