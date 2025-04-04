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
from psyclone.transformations import ACCLoopTrans, OMPLoopTrans
from psytran.loop import _check_loop

__all__ = [
    "apply_parallel_directive",
    "has_parallel_directive",
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


def apply_parallel_directive(block, directive_cls, options=None):
    """
    Apply an directive to a block of code.

    :arg block: the block of code to apply the directive to.
    :type block: :py:class:`list`
    :arg directive_cls: the type of directive
    :type directive_cls: :py:class:`psyclone.psyir.transformations.\
        parallel_loop_trans.ParallelLoopTrans.__class__`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`

    :raises TypeError: if the options argument is not a dictionary.
    """
    if options is None:
        options = {}
    print("hello")
    if not isinstance(options, dict):
        raise TypeError(f"Expected a dict, not '{type(options)}'.")
    directive_cls().apply(block, options=options)


def has_parallel_directive(node, directive_cls):
    """
    Determine whether a node is inside a parallel directive of a given type.

    :arg node: the Node to check.
    :type node: :py:class:`Node`
    :arg directive_cls: the type of directive
    :type directive_cls: :py:class:`psyclone.psyir.transformations.\
        parallel_loop_trans.ParallelLoopTrans.__class__`

    :returns: ``True`` if the Node has a parallel directive, else ``False``.
    :rtype: :py:class:`bool`
    """
    if isinstance(node, Iterable):
        return has_parallel_directive(node[0], directive_cls)
    assert isinstance(node, nodes.Node)
    return bool(node.ancestor(directive_cls))


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
        if not has_parallel_directive(loop, ACCKernelsDirective):
            raise ValueError(
                "Cannot apply an ACC loop directive without a kernels "
                "directive."
            )
    if isinstance(directive, OMPLoopTrans):
        if has_parallel_directive(loop, ACCKernelsDirective):
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
    assert isinstance(loop, nodes.Loop)
    if isinstance(
        loop.parent.parent, ACCLoopDirective
    ) and has_parallel_directive(loop, ACCKernelsDirective):
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
