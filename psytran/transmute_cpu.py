# (C) Crown Copyright 2025, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

'''
Top level function(s) intended to be callable by
PSyclone Transmute global and override functions.
'''

from __future__ import print_function
from psyclone.psyir.nodes import Loop
from psytran.family import (
    update_ignore_list,
    check_omp_ancestry,
    span_parallel,
    try_transformation)
from psytran.transmute_rules import (
    OverridesClass,
    validate_rules)
from psytran.prop_trans import PropTrans

__all__ = [
    "try_loop_omp_pardo"
]


def try_loop_omp_pardo(loop_node,
                       override_class
                       ):
    '''
    Called inside a loop running through the files schedule, and processing
    each loop one at a time, which occurs here.

    First it checks if a list of ignore dependencies objects has been provided

    Then it spans some parallel regions

    Then it adds in either parallel do or do clause to the loop node

    OpenMP ancestry for the loop is checked where relevant.

    :arg loop_node: The Loop node to transform
    :type loop_node: :py:class:`Loop`
    :arg override_class:  Class containing a list of override classes to check
                          against for an ignore_dependencies_for list, etc.
                          Also contains master override settings.
    :type OverridesClass: :py:class:`OverridesClass`
    '''

    if not isinstance(loop_node, Loop):
        raise TypeError(f"Expected a loop node \
                        '{type(Loop)}'.")

    if not isinstance(override_class, OverridesClass):
        raise TypeError(f"Expected a tag_override object, not \
                        '{type(override_class)}'.")

    # options dict setup
    options = {}

    trans = PropTrans()

    # If there is an loop_tag_overrides_list, work through the objects
    # and update the options ignore_dependencies_for with tags where the
    # loop tags match
    options = update_ignore_list(loop_node, options, override_class)

    # Check if the ancestry for a omp_transform_par_do and a
    # omp_transform_do transformation is correct for the given node
    # We expect there to be no parallel ancestry for either transformation
    # when we are attempting to span a parallel region.
    if (not check_omp_ancestry(loop_node, trans.omp_transform_par_do()) or
            check_omp_ancestry(loop_node, trans.omp_transform_do())):
        span_parallel(loop_node, override_class.get_loop_max_qty())

    # Given whether the loop is now currently in a parallel section
    # change the OMP transformation to the correct option.
    # Either parallel do, if there is no parallel region above
    # or do
    # check_omp_ancestry for the omp_transform_do will return false if there
    # is a parallel section for a omp_transform_do transformation
    # default transformation will be parallel do
    if not check_omp_ancestry(loop_node, trans.omp_transform_do()):
        transformation = trans.omp_transform_do()
    else:
        transformation = trans.omp_transform_par_do()

    # Check the ability to transform given OMP ancestry
    if not check_omp_ancestry(loop_node, transformation):

        loop_continue, options = validate_rules(loop_node, options)

        # Given the rule checks above, if they are all clear
        if loop_continue:
            # Try the transformation - either a OMP parallel do or do
            error = try_transformation(loop_node, transformation, options)
            print(error)
