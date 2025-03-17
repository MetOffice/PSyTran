# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

r"""
This module implements functions for querying whether code blocks and
:py:class:`Loop`\s have OpenACC directives associated with them, as well as for
applying such directives.
"""

from collections.abc import Iterable
from psyclone.psyir import nodes
from psyclone.psyir.nodes import (
    ACCKernelsDirective,
    ACCLoopDirective,
    OMPDoDirective,
    OMPLoopDirective,
    OMPParallelDoDirective,
    OMPTeamsDistributeParallelDoDirective,
    OMPTeamsLoopDirective,
)
from psyclone.psyir.transformations import ACCKernelsTrans
from psyclone.transformations import ACCLoopTrans, OMPLoopTrans
from psytran.loop import _check_loop

__all__ = [
    "apply_acc_kernels_directive",
    "has_acc_kernels_directive",
    "apply_loop_directive",
    "has_loop_directive",
]


def _check_directive(directive):
    """
    Determine whether the directive to be applied is supported by PSyclone.

    :arg directive: the directive to check.
    :type directive: :py:class:`Directive`

    :raises: ValueError: if the directive is not a PSyclone loop trans object.
    """
    if not isinstance(directive, (ACCLoopTrans, OMPLoopTrans)):
        raise ValueError(
            f"Supplied directive type is not a supported loop directive, "
            f"found {type(directive)}"
        )


def apply_acc_kernels_directive(block, options=None):
    """
    Apply an ACC ``kernels`` directive to a block of code.

    :arg block: the block of code to apply the directive to.
    :type block: :py:class:`list`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`

    :raises TypeError: if the options argument is not a dictionary.
    """
    if options is not None and not isinstance(options, dict):
        raise TypeError(f"Expected a dict, not '{type(options)}'.")
    ACCKernelsTrans().apply(block, options=options)


def has_acc_kernels_directive(node):
    """
    Determine whether a node is inside an ACC ``kernels`` directive.

    :arg node: the Node to check.
    :type node: :py:class:`Node`

    :returns: ``True`` if the Node has a ``kernels`` directive, else ``False``.
    :rtype: :py:class:`bool`
    """
    if isinstance(node, Iterable):
        return has_acc_kernels_directive(node[0])
    assert isinstance(node, nodes.Node)
    return bool(node.ancestor(ACCKernelsDirective))


def apply_loop_directive(loop, directive, options=None):
    """
    Apply a ``loop`` directive.

    :arg loop: the Loop Node to apply the directive to.
    :type loop: :py:class:`Loop`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`

    :raises TypeError: if the options argument is not a dictionary.
    :raises ValueError: if a ``kernels`` directive has not yet been applied to
    a kernel trying to apply an ACC ``loop`` directive.
    """
    # Check options is valid
    if options is not None and not isinstance(options, dict):
        raise TypeError(f"Expected a dict, not '{type(options)}'.")
    # Check directive is valid/supported
    _check_directive(directive)
    # Check loop is valid
    _check_loop(loop)

    if isinstance(directive, ACCLoopTrans):
        if not has_acc_kernels_directive(loop):
            raise ValueError(
                "Cannot apply an ACC loop directive without a kernels "
                "directive."
            )
    if isinstance(directive, OMPLoopTrans):
        if has_acc_kernels_directive(loop):
            raise ValueError(
                "Cannot apply an OMP loop directive to a kernel with an "
                "ACC kernels directive."
            )

    directive.apply(loop, options=options)


def has_loop_directive(loop):
    """
    Determine whether a node has an OpenACC ``loop`` directive.

    :arg loop: the Loop Node to check.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Node has a ``loop`` or ``do`` directive,
              else ``False``.
    :rtype: :py:class:`bool`
    """
    print(loop.parent.parent)
    assert isinstance(loop, nodes.Loop)
    if isinstance(
        loop.parent.parent, ACCLoopDirective
    ) and has_acc_kernels_directive(loop):
        return True
    if isinstance(
        loop.parent.parent,
        (
            OMPDoDirective,
            OMPLoopDirective,
            OMPParallelDoDirective,
            OMPTeamsDistributeParallelDoDirective,
            OMPTeamsLoopDirective,
        ),
    ):
        return True

    return False
