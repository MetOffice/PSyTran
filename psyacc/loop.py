from psyclone.psyir import nodes
from psyclone.nemo import NemoKern
from psyclone.transformations import ACCLoopDirective, ACCLoopTrans
from psyacc.kernels import has_kernels_directive, is_outer_loop

__all__ = [
    "has_loop_directive",
    "apply_loop_directive",
    "is_perfectly_nested",
    "is_simple_loop",
    "get_loop_variable_name",
    "get_loop_nest_variable_names",
]


def has_loop_directive(node):
    """
    Determine whether a node has an OpenACC ``loop`` directive.
    """
    assert isinstance(node, nodes.Node)
    return isinstance(node.parent.parent, ACCLoopDirective)


def apply_loop_directive(loop, options={}):
    """
    Apply a ``loop`` directive.

    :arg loop: the :class:`Loop` node.
    :kwarg options: a dictionary of clause options.
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    if not isinstance(options, dict):
        raise TypeError(f"Expected a dict, not '{type(options)}'.")
    if not has_kernels_directive(loop):
        raise ValueError("Cannot apply a loop directive without a kernels directive.")
    ACCLoopTrans().apply(loop, options=options)


def is_perfectly_nested(loop):
    """
    Determine whether a loop nest is perfectly nested, i.e., each level except
    the deepest contains only the next loop.

    :arg loop: the outer-most loop of the nest
    """
    if not isinstance(loop, nodes.Loop):
        raise TypeError(f"Expected a Loop, not '{type(loop)}'.")
    loops = loop.walk(nodes.Loop)
    depth = loop.depth
    for i in range(1, len(loops)):
        depth += 2
        child_nodes = loops[i].walk(nodes.Node)
        nodes_at_depth = [node for node in child_nodes if node.depth == depth]
        if len(nodes_at_depth) != 1:
            return False
        assert isinstance(nodes_at_depth[0], nodes.Loop)
    else:
        return True


def is_simple_loop(loop):
    """
    Determine whether a loop nest is simple, i.e., perfectly nested, with a
    single assignment at the deepest level.

    :arg loop: the outer-most loop of the nest
    """
    if not is_perfectly_nested(loop):
        return False
    innermost_loop = loop.walk(nodes.Loop)[-1]
    depth = innermost_loop.depth
    child_nodes = innermost_loop.walk(nodes.Node)
    nodes_next = [node for node in child_nodes if node.depth == depth + 2]
    if len(nodes_next) != 1 or not isinstance(nodes_next[0], NemoKern):
        return False
    nodes_next = [node for node in child_nodes if node.depth == depth + 4]
    return len(nodes_next) == 1 and isinstance(nodes_next[0], nodes.Assignment)


def get_loop_variable_name(loop):
    """
    Given a :class:`Loop` node, return its variable name.
    """
    assert isinstance(loop, nodes.Loop)
    return loop.variable.name


def get_loop_nest_variable_names(loop):
    """
    Given a :class:`Loop` node, return the variable names of each loop it
    contains.
    """
    assert isinstance(loop, nodes.Loop)
    return [get_loop_variable_name(loop) for loop in loop.walk(nodes.Loop)]
