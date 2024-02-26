# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes
from psyacc.family import get_descendents

__all__ = ["is_character", "refers_to_character"]


def is_character(ref):
    """
    Determine whether a Reference Node is of type `CHARACTER`.

    :arg ref: the Node to check.
    :type ref: :py:class:`Reference`
    """
    assert isinstance(ref, nodes.Reference)
    return "CHARACTER" in ref.datatype.type_text


def refers_to_character(node):
    r"""
    Determine whether a Node contains references to `CHARACTER`\s.

    :arg node: the Node to check.
    :type node: :py:class:`Node`
    """
    return any([is_character(ref) for ref in get_descendents(node, nodes.Reference)])
