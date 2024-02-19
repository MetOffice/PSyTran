# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyacc.family import get_descendents

__all__ = ["is_character", "refers_to_character"]


def is_character(node):
    """
    Determine whether a :class:`psyclone.psyir.nodes.reference.Reference` has Fortran
    type `CHARACTER`.
    """
    assert isinstance(node, nodes.Reference)
    return "CHARACTER" in node.datatype.type_text


def refers_to_character(node):
    r"""
    Determine whether a :class:`psyclone.psyir.nodes.node.Node` contains references to
    Fortran `CHARACTER`\s.
    """
    return any([is_character(ref) for ref in get_descendents(node, nodes.Reference)])
