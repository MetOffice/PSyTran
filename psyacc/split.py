from psyacc.family import is_next_sibling

__all__ = ["split_consecutive"]


def split_consecutive(block):
    """
    Given a block of nodes at some depth, separate out those which follow one
    another.
    """
    blocks = {}
    current = {}
    for node in block:
        depth = node.depth
        if node.depth not in blocks:
            blocks[depth] = []
        if node.depth not in current:
            current[depth] = [node]
            continue

        previous = current[depth][-1]
        if is_next_sibling(previous, node):
            current[depth].append(node)
        else:
            blocks[depth].append(current)
            current[depth] = [node]

    ret = []
    for depth, values in current.items():
        if len(values) > 0:
            blocks[depth].append(values)
        ret += blocks[depth]
    return ret
