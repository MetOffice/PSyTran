# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

from psyclone.psyir import nodes

__all__ = [
    "get_descendents",
    "get_ancestors",
    "get_children",
    "get_parent",
    "get_siblings",
    "has_descendent",
    "has_ancestor",
    "are_siblings",
    "is_next_sibling",
]


def get_descendents(
    node, node_type=nodes.Node, inclusive=False, exclude=(), depth=None
):
    """
    Get all ancestors of a node with a given type.

    :arg node: the node to search for descendents of.
    :kwarg node_type: the type of node to search for.
    :kwarg inclusive: if ``True``, the current node is included.
    :kwarg exclude: type(s) of node to exclude.
    :kwarg depth: specify a depth for the descendents to have.
    """
    assert isinstance(node, nodes.Node), f"Expected a Node, not '{type(node)}'."
    assert isinstance(inclusive, bool), f"Expected a bool, not '{type(inclusive)}'."
    assert isinstance(node_type, tuple) or issubclass(node_type, nodes.Node)
    if depth is not None:
        assert isinstance(depth, int), f"Expected an int, not '{type(depth)}'."
    return [
        descendent
        for descendent in node.walk(node_type, depth=depth)
        if not isinstance(descendent, exclude) and (inclusive or descendent is not node)
    ]


def get_ancestors(node, node_type=nodes.Loop, inclusive=False, exclude=(), depth=None):
    """
    Get all ancestors of a node with a given type.

    :arg node: the node to search for ancestors of.
    :kwarg node_type: the type of node to search for.
    :kwarg inclusive: if ``True``, the current node is included.
    :kwarg exclude: type(s) of node to exclude.
    :kwarg depth: specify a depth for the ancestors to have.
    """
    assert isinstance(node, nodes.Node), f"Expected a Node, not '{type(node)}'."
    assert isinstance(inclusive, bool), f"Expected a bool, not '{type(inclusive)}'."
    assert isinstance(node_type, tuple) or issubclass(node_type, nodes.Node)
    if depth is not None:
        assert isinstance(depth, int), f"Expected an int, not '{type(depth)}'."
    ancestors = []
    node = node.ancestor(node_type, excluding=exclude, include_self=inclusive)
    while node is not None:
        ancestors.append(node)
        node = node.ancestor(node_type, excluding=exclude)
    if depth is not None:
        ancestors = [a for a in ancestors if a.depth == depth]
    return ancestors


def get_children(node, node_type=nodes.Node, exclude=()):
    """
    Get all immediate descendents of a node with a given type, i.e., those at
    the next depth level.

    :arg node: the node to search for descendents of.
    :kwarg node_type: the type of node to search for.
    :kwarg exclude: type(s) of node to exclude.
    """
    assert isinstance(node, nodes.Node), f"Expected a Node, not '{type(node)}'."
    if not isinstance(node_type, tuple):
        issubclass(node_type, nodes.Node)
        node_type = (node_type,)
    children = [
        grandchild
        for child in node.children
        for grandchild in child.children
        if isinstance(grandchild, node_type) and not isinstance(grandchild, exclude)
    ]
    return children


def get_parent(node):
    """
    Get the immediate ancestor of a node.

    :arg node: the node to search for ancestors of.
    """
    assert isinstance(node, nodes.Node), f"Expected a Node, not '{type(node)}'."
    parent = node.parent.parent
    return parent


def get_siblings(node, node_type=nodes.Node, inclusive=False, exclude=()):
    """
    Get all nodes with a given type at the same depth level.

    :arg node: the node to search for siblings of.
    :kwarg node_type: the type of node to search for.
    :kwarg inclusive: if ``True``, the current node is included.
    :kwarg exclude: type(s) of node to exclude.
    """
    return [
        sibling
        for sibling in node.siblings
        if isinstance(sibling, node_type)
        and not isinstance(sibling, exclude)
        and (inclusive or sibling is not node)
    ]


def has_descendent(node, node_type, inclusive=False):
    """
    Check whether a node has a descendent node with a given type.

    :arg node: the node to check for descendents of.
    :arg node_type: the type of node to search for.
    :kwarg inclusive: if ``True``, the current node is included.
    """
    return bool(get_descendents(node, inclusive=inclusive, node_type=node_type))


def has_ancestor(node, node_type=nodes.Loop, name=None, inclusive=False):
    """
    Check whether a node has an ancestor node with a given type.

    :arg node: the node to check for ancestors of.
    :kwarg inclusive: if ``True``, the current node is included.
    :kwarg node_type: the type of node to search for.
    :kwarg name: check whether the node has an ancestor with a particular name.
    """
    ancestors = get_ancestors(node, inclusive=inclusive, node_type=node_type)
    if name:
        return any([ancestor.variable.name == name for ancestor in ancestors])
    return bool(ancestors)


def are_siblings(*nodes):
    r"""
    Determine whether a collection of :class:`psyclone.psyir.nodes.node.Node`\s have the
    same parent.
    """
    assert len(nodes) > 1
    return all([node in nodes[0].siblings for node in nodes])


def is_next_sibling(node1, node2):
    """
    Determine whether one :class:`psyclone.psyir.nodes.node.Node` immediately follows
    another.

    :arg node1: the first node.
    :arg node2: the second node.
    """
    return node2.immediately_follows(node1)
