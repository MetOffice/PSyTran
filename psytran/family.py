# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
r"""
This module provides functions for determining the ancestors and descendents of
:py:class:`Node`\s, as well as for querying their existence and nature.
"""

from psyclone.psyir.nodes import (
    Loop, Node, Assignment, Schedule,
    ArrayOfStructuresReference,
    IfBlock,
    OMPDoDirective,
    OMPParallelDirective,
    OMPParallelDoDirective)
from psyclone.psyGen import Transformation
from psyclone.transformations import TransformationError
from psytran.prop_trans import PropTrans


__all__ = [
    "get_descendents",
    "get_ancestors",
    "get_children",
    "has_descendent",
    "has_ancestor",
    "child_valid_trans",
    "check_omp_ancestry",
    "get_last_child_shed",
    "span_check_loop",
    "span_parallel",
    "string_match_ref_var",
    "strip_index",
    "get_reference_tags",
    "try_transformation",
    "try_validation",
    "update_ignore_list",
    "work_out_collapse_depth"
]


def get_descendents(
    node, node_type=Node, inclusive=False, exclude=(), depth=None
):
    """
    Get all ancestors of a Node with a given type.

    :arg node: the Node to search for descendents of.
    :type node: :py:class:`Node`
    :kwarg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg inclusive: if ``True``, the current node is included.
    :type inclusive: :py:class:`bool`
    :kwarg exclude: type(s) of node to exclude.
    :type exclude: :py:class:`bool`
    :kwarg depth: specify a depth for the descendents to have.
    :type depth: :py:class:`int`

    :returns: list of descendents according to specifications.
    :rtype: :py:class:`list`
    """
    assert isinstance(node, Node), f"Expected a Node, not '{type(node)}'."
    assert isinstance(
        inclusive, bool
    ), f"Expected a bool, not '{type(inclusive)}'."
    assert isinstance(node_type, tuple) or issubclass(node_type, Node)
    if depth is not None:
        assert isinstance(depth, int), f"Expected an int, not '{type(depth)}'."
    return [
        descendent
        for descendent in node.walk(node_type, depth=depth)
        if not isinstance(descendent, exclude)
        and (inclusive or descendent is not node)
    ]


def get_ancestors(
    node, node_type=Loop, inclusive=False, exclude=(), depth=None
):
    """
    Get all ancestors of a Node with a given type.

    :arg node: the Node to search for ancestors of.
    :type node: :py:class:`Node`
    :kwarg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg inclusive: if ``True``, the current node is included.
    :type inclusive: :py:class:`bool`
    :kwarg exclude: type(s) of node to exclude.
    :type exclude: :py:class:`bool`
    :kwarg depth: specify a depth for the ancestors to have.
    :type depth: :py:class:`int`

    :returns: list of ancestors according to specifications.
    :rtype: :py:class:`list`
    """
    assert isinstance(node, Node), f"Expected a Node, not '{type(node)}'."
    assert isinstance(
        inclusive, bool
    ), f"Expected a bool, not '{type(inclusive)}'."
    assert isinstance(node_type, tuple) or issubclass(node_type, Node)
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


def get_children(node, node_type=Node, exclude=()):
    """
    Get all immediate descendents of a Node with a given type, i.e., those at
    the next depth level.

    :arg node: the Node to search for descendents of.
    :type node: :py:class:`Node`
    :kwarg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg exclude: type(s) of node to exclude.
    :type exclude: :py:class:`bool`

    :returns: list of children according to specifications.
    :rtype: :py:class:`list`
    """
    assert isinstance(node, Node), f"Expected a Node, not '{type(node)}'."
    if not isinstance(node_type, tuple):
        issubclass(node_type, Node)
        node_type = (node_type,)
    children = [
        grandchild
        for child in node.children
        for grandchild in child.children
        if isinstance(grandchild, node_type)
        and not isinstance(grandchild, exclude)
    ]
    return children


def has_descendent(node, node_type, inclusive=False):
    """
    Check whether a Node has a descendent node with a given type.

    :arg node: the Node to check for descendents of.
    :type node: :py:class:`Node`
    :arg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg inclusive: if ``True``, the current node is included.
    :type inclusive: :py:class:`bool`

    :returns: ``True`` if there are descendents meeting specifications, else
        ``False``.
    :rtype: :py:class:`bool`
    """
    return bool(
        get_descendents(node, inclusive=inclusive, node_type=node_type)
    )


def has_ancestor(node, node_type=Loop, inclusive=False, name=None):
    """
    Check whether a Node has an ancestor node with a given type.

    :arg node: the Node to check for ancestors of.
    :type node: :py:class:`Node`
    :kwarg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg inclusive: if ``True``, the current node is included.
    :type inclusive: :py:class:`bool`
    :kwarg name: check whether the node has an ancestor with a particular name.
    :type name: :py:class:`str`

    :returns: ``True`` if there are ancestors meeting specifications, else
        ``False``.
    :rtype: :py:class:`bool`
    """
    ancestors = get_ancestors(node, inclusive=inclusive, node_type=node_type)
    if name:
        return any(ancestor.variable.name == name for ancestor in ancestors)
    return bool(ancestors)


def child_valid_trans(check_current_node):
    '''
    We want to see if the loop could be parallelised with a
    pardo transformation. Given we are going all the way down
    the tree in the wider loop, we have to do this manually here.
    We check the current loop to see if it can be pardo.
    Checks are standard checks (ignoring OMP ancestry
    as this is done at the top level).

    '''
    valid_loop = False

    # Setup
    options = {}
    trans = PropTrans()

    loop_child_list = get_descendents(check_current_node, Loop)

    # If there is a list of loops
    if loop_child_list:
        # If the current node is a loop, we want to check it to, first
        if isinstance(check_current_node, Loop):
            loop_child_list.insert(0, check_current_node)

        for loop in loop_child_list:
            # If additional rules grow for checking what is a valid loop
            # they may need to go here too on a case by case basis.
            # Checking for the array of structs it not needed, as we can still
            # parallelise something there.
            options = work_out_collapse_depth(loop, options)

            # Call the validation instead of try_transformation
            error = try_validation(loop, trans.omp_transform_par_do(), options)

            # IF there are no errors, continue, otherwise exit
            if len(error) == 0 or error == "":
                valid_loop = True
            else:
                valid_loop = False
                break

    # Return number of children spanning over also
    # Used in in rule for no of loops spanning over
    if valid_loop:
        ret_child_loop_qty = len(loop_child_list)
    else:
        ret_child_loop_qty = 0

    return valid_loop, ret_child_loop_qty


def check_omp_ancestry(
    node_target: Node,
    transformation: Transformation,
):
    '''
    Check the OMP ancestry, both for spanning parallel or
    parallel do. Returns True, which will stop future transformations
    from occurring.
    If the transformation to apply is a simple OMP do then we instead
    expect the presence of a parallel region, and therefore will
    return false.
    Due to psyir tree returning sibling loop ancestors during psyclone,
    also check the path to each OMP parallel.
    If there is a path to both, that is incorrect.
    See the list of exceptions below.
    '''

    # Store whether there is a current Loop and a
    # OMP Parallel, Parallel Do or Do ancestor
    omp_ancestor_par = node_target.ancestor(OMPParallelDirective)
    omp_ancestor_par_do = node_target.ancestor(OMPParallelDoDirective)
    omp_ancestor_do = node_target.ancestor(OMPDoDirective)

    # There seems to be an issue in PSyclone where the presence of an OMP
    # parallel section.
    # Under the same parent node is causing a little confusion.
    # The paths allow us to check index references for closeness
    # Given a certain circumstance we can iron out the confusion
    # Needs to be wrapped in a try else it fails
    try:
        path_to_omp_par = node_target.path_from(omp_ancestor_par)
    except ValueError:
        path_to_omp_par = False
    try:
        path_to_omp_par_do = node_target.path_from(omp_ancestor_par_do)
    except ValueError:
        path_to_omp_par_do = False

    # DEFAULT result
    # The default presence of OMP given the below ancestry
    # True : There is an OpenMP Parallel section above the node,
    #        This can be either a Parallel or Parallel Do section above
    #        The default intended use is if this is True, do not do an
    #        OpenMP transformation.
    # False : There is no OpenMP Parallel sections detected above.
    if ((omp_ancestor_par and path_to_omp_par)
            or (omp_ancestor_par_do and path_to_omp_par_do)):
        print("Parallel OMP region ancestor found")
        omp_ancestry_presence = True
    else:
        omp_ancestry_presence = False

    # When adding a OpenMP DO transformation, it's a little more nuanced.
    # We will in principle reverse the result.
    # True : There is an OpenMP Parallel Do section above the node.
    # False : There is a Parallel section above the Node, and it is safe.
    if transformation.omp_directive == "do":
        # A OpenMP do transformation needs a parallel section above,
        # it checks and corrects.
        # An occurrence where adjacent parallel do regions are being
        # picked up and the parallel ancestor is misreporting. Therefore,
        # if there a parallel ancestor and path, but there is not a path to a
        # parallel do reference node. Checking the paths mitigates this
        # occurrence. To be reported to STFC as a bug in psyclone.
        if omp_ancestor_par and path_to_omp_par and not path_to_omp_par_do:
            print("Adjacent node detected in Ancestry")
            print("Parallel OMP region ignored as transformation is OMP do")
            omp_ancestry_presence = False

        # If there is no path to both an parallel or parallel do Node,
        # but it has reported an parallel ancestor
        if not omp_ancestor_par and not path_to_omp_par:
            print("No Parallel region present, cannot try do")
            omp_ancestry_presence = True

        # This stops the nesting of OMP do under parallel sections
        # If there is one already present, it will effectively understand the
        # above a parallel and a do, which we don't want to try parallelism in
        # this occurrence.
        if omp_ancestor_do:
            omp_ancestry_presence = True

    return omp_ancestry_presence


def get_last_child_shed(loop_node):
    '''
    Get the last child loop schedule of the provided node.
    Then we can do some checks on it
    '''

    loop_list = []

    # Set to false if a Schedule cannot be found
    ret_shed = None

    # Work through the schedule of the node
    # The first one will be the schedule of this loop
    loop_shed_list = loop_node.walk(Schedule)
    loop_list = loop_shed_list[0].walk(Loop)

    # If there is a list of loops for this schedule
    if loop_list:
        # Get the last element and walk it's schedule
        last_element = len(loop_list)-1
        shed_list = loop_list[last_element].walk(Schedule)
        if shed_list:
            # Return the first schedule for this loop.
            ret_shed = shed_list[0]

    return ret_shed


def span_check_loop(child_list, start_index_loop, loop_max_qty):
    '''
    Run through child_list from the provided start index.
    Check each node.
    If it is an If block or a Loop node, check loops, self
    and children. These loops are checked against their own set
    of rules and a provided limit from the override.
    '''

    trans = PropTrans()

    # Setup for loop
    last_good_index = 0
    loop_child_qty = 0

    # Assume we are unable to span a region if nothing is found
    parallel_possible = False

    # Work through the child list of nodes of the given ancestor
    # Starting at the current node, ending at the last child node
    # The goal of the loop is to find the most appropriate end node for
    # a parallel region. It will check all of the loops present in the
    # current proposed parallel region can be transformed.
    # As soon as one cannot be, it ends the loop, leaving the end index
    # as the previous step through the loop.
    for index in range(start_index_loop, len(child_list)-1):
        check_current_node = child_list[index]

        # reset each loop
        try_parallel = False

        assignment_cont = False

        # If its an assignment we want to continue to the next index to check
        # but not try a parallel region. This way they can be included in the
        # spanning region, but will not be the start or end nodes.
        # May need to be adjusted in the future
        if isinstance(check_current_node, Assignment):
            assignment_cont = True

        # If the node is an if block or loop,
        # check all of the loops could be OpenMP
        # parallel do normally, as a safety check for the region as a whole.
        if isinstance(check_current_node, (IfBlock, Loop)):
            ret_child_qty = 0
            try_parallel, ret_child_qty = child_valid_trans(check_current_node)
            # Add more checks here and keep setting try_parallel or similar
            if try_parallel:
                loop_child_qty = loop_child_qty + ret_child_qty

        if loop_child_qty > loop_max_qty:
            break

        # if the node is a loop, if or assignment, we want to continue
        # we've checked as to whether to loop children are good to parallelise
        # if it's an assignment node, we want to continue the loop,
        # but go no further with the checks.
        if try_parallel or assignment_cont:
            # Leave these if checks in place, try_parallel and else,
            # index > start_index_loop, they work well
            # If the node loop children are good, and it's not the first node
            if try_parallel:
                if index > start_index_loop:
                    check_span_nodes = []
                    # Surely we should be checking the current index?
                    for index_inner in range(start_index_loop, index+1):
                        check_span_nodes.append(child_list[index_inner])
                    # Try the transformation
                    error = try_validation(
                        check_span_nodes,
                        trans.omp_parallel(), {})
                    # If there is an error, we cannot do this one and
                    # should break
                    if len(error) == 0 or error == "":
                        parallel_possible = True
                        last_good_index = index
                    else:
                        print(error)
                        break
        else:
            break

    return parallel_possible, last_good_index


def span_parallel(loop_node, loop_max_qty):
    '''
    Transformation used is omp_parallel. Span a parallel section.
    Get the ancestor node of the provided node, then grab it's children.
    This is a list of all nodes, including the provided node.
    This provided node will be the first node checked.
    '''

    trans = PropTrans()

    # Find the ancestor schedule.
    # Given all of this stems from the first loop
    # There is an occurrence where this needs to stem
    # from the first if above a loop
    # so far no adverse effects of doing so
    if_loop_ancestor = loop_node.ancestor(IfBlock)
    if if_loop_ancestor:
        shared_ancestor = if_loop_ancestor.ancestor(Schedule)
        check_node = if_loop_ancestor
    # Otherwise get an reference to the ancestor schedule
    # Even the top loop, who's ancestor is a subroutine
    # Or similar, will
    else:
        shared_ancestor = loop_node.ancestor(Schedule)
        check_node = loop_node

    # Get the child list of the ancestors schedule
    # This will be used to have a list of potential nodes
    # to span over ready.
    child_list = shared_ancestor.children

    # Work through the list, until we meet the node which is
    # the current origin in the schedule of the ancestor.
    # This will be the first index node which a potential
    # parallel region is spanned from.
    start_index_loop = 0
    for index, node in enumerate(child_list):
        if check_node == node:
            start_index_loop = index
            # We only want the start, we can exit the loop
            break

    # Check each node in the child list
    # Check all loop nodes under each node (including node if is a loop)
    parallel_possible, last_good_index = span_check_loop(child_list,
                                                         start_index_loop,
                                                         loop_max_qty)

    # The final attempt to see if parallel region is possible
    # Given these indexes have been validated, it should be
    if parallel_possible:
        span_nodes = []
        for index_inner in range(start_index_loop, last_good_index+1):
            span_nodes.append(child_list[index_inner])
        if len(span_nodes) > 1:
            # Try the transformation
            error = try_transformation(span_nodes, trans.omp_parallel(), {})
            # Confirm success and advise which nodes
            if len(error) == 0 or error == "":
                print("Spanning Parallel over:")
                print(span_nodes)


def string_match_ref_var(loop_node):
    '''
    We need to check the metadata of whether references of a
    loop node match to certain properties.
    Return True, if a Array of types (or ArrayOfStructures)
    is found.
    ArrayOfStructures is a good reference to find, it notes
    that there is an array of objects in the children that is accessed
    in the loop body, likely better being parallelised differently.
    Therefore if we find this match, we want to skip it.
    '''

    # get the last child schedule, only do work if shed exists
    last_child_shed = get_last_child_shed(loop_node)

    struct_ref_exists = False

    if last_child_shed:
        reference_tags = []
        for struct_ref in last_child_shed.walk(ArrayOfStructuresReference):
            struct_ref_exists = True
            reference_tags.extend(get_reference_tags(struct_ref))

        # Only do the work if ArrayOfStructuresReference exists
        if struct_ref_exists:
            variable_tags = get_reference_tags(loop_node)
            # The first is the current indexer of the loop
            # If the loop index is in the indexes found related to the
            # ArrayOfStructures reference, then we've found a match
            if variable_tags[0] in reference_tags:
                return True

    return False


def strip_index(line, str_tag):
    '''
    Run through the provided string line from a schedule, and
    strip the line at the given tag down to just an index.
    There does not seem to be an alterative method in PSYIR
    to return just this property. In order to check a
    struct (type) that is accessed by a list, this is method
    required.
    '''

    breakout_string = line.partition(str_tag)
    # We know it's the start of the array, given the str_tag
    indexer_list = breakout_string[2].split(",")
    # formatting
    indexer_ref = indexer_list[0]
    # A list of characters which will be removed from strings.
    for char in ["[", "]", "'"]:
        indexer_ref = indexer_ref.replace(char, "")

    # return the index without any clutter
    return indexer_ref


def get_reference_tags(node):
    '''
    Extracts tags found in schedules for different node types
    '''
    # Create our empty list to store reference tags
    reference_tags = []

    # get the reference the hard way as we cannot seem to
    # access it directly
    information = str(node)
    array_info = information.splitlines()

    if isinstance(node, ArrayOfStructuresReference):
        # Work through each line of the struct_ref turned into a str
        for line in array_info:
            # If there is a Reference, this is what we are going to
            # manipulate to gather out the index reference
            if ("Reference[name:" in line and
                    "ArrayOfStructures" not in line):
                reference_tags.append(strip_index(
                    line, "Reference[name:"))

    elif isinstance(node, Loop):
        for line in array_info:
            if "Loop[variable:" in line:
                reference_tags.append(strip_index(
                    line, "Loop[variable:"))

    else:
        raise TypeError(f"Node of type {type(node)} not currently supported "
                        f"for extracting tags")

    return reference_tags


def try_transformation(
    node_target: Node,
    transformation: Transformation,
    options: dict = None
):
    '''
    Try the provided transformation provided.
    Otherwise raise an error which is returned.
    The try transformation is present is all transformations for OMP,
    so it has been made generic and called by most below.

    :arg node_target: The Node to transform - Can instead be provided
                        as a list of nodes to apply.
    :type node_target: :py:class:`Node`
    :arg transformation: The transformation to apply
    :type transformation: :py:class:`Transformation`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`
    '''

    if options is None:
        options = {}

    error_message = ""

    try:
        print("Trying")
        transformation.apply(node_target, options=options)

    except (TransformationError, IndexError) as err:
        error_message = str(err)
        print(f"Could not transform "
              f"because:\n{error_message}")

    return error_message


def try_validation(
    node_target: Node,
    transformation: Transformation,
    options: dict = None
):
    '''
    Try the provided transformation provided.
    Instead with a validate as opposed to apply
    Otherwise raise an error which is returned.
    The try transformation is present is all transformations for OMP,
    so it has been made generic and called by most below.

    :arg node_target: The Node to transform - Can instead be provided
                        as a list of nodes to apply.
    :type node_target: :py:class:`Node`
    :arg transformation: The transformation to apply
    :type transformation: :py:class:`Transformation`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`
    '''

    if options is None:
        options = {}

    error_message = ""

    try:
        transformation.validate(node_target, options=options)

    except (TransformationError, IndexError) as err:
        error_message = str(err)
        print(f"Could not transform "
              f"because:\n{error_message}")

    return error_message


def update_ignore_list(
                    loop_node,
                    current_options,
                    override_class
                    ):
    '''
    Pass in a loop_node and array of loop_tag_overrides objects.
    Check each object and if the tag matches the loop, check the
    know list, and append new options.
    '''

    # Setup References
    loop_tag = str(loop_node.loop_type)
    current_ignore_list = []

    overrides = override_class.get_tag_overrides()
    if overrides:
        for override_obj in overrides:
            if loop_tag == override_obj.get_loop_tag():
                override_options = override_obj.options()
                if "ignore_dependencies_for" in override_options:
                    current_ignore_list.append(
                        override_options["ignore_dependencies_for"])

    current_options["ignore_dependencies_for"] = current_ignore_list

    return current_options


def work_out_collapse_depth(loop_node, options):
    '''
    Generate a value for how many collapses to specifically
    do given the number of children.
    '''

    # The default number of loops is 1 given self
    n_collapse = 1
    # Are there any loop children, will return array of child
    # nodes.
    child_loop_list = get_descendents(loop_node, Loop)
    if child_loop_list:
        # Add the length of the node array, or the number of
        # to the n_collapse value to return
        n_collapse = n_collapse + len(child_loop_list)

    if n_collapse > 1:
        options["collapse"] = n_collapse

    return options
