# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes

__all__ = ["is_literal_assignment"]


def is_literal_assignment(node):
    """
    Determine whether a Node corresponds to an assignment of a literal value.

    :arg node: the :class:`psyclone.psyir.nodes.node.Node` in question
    """
    return isinstance(node, nodes.Assignment) and isinstance(node.rhs, nodes.Literal)
