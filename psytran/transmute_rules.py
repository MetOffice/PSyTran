# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
'''
File to cohabitate all rules relating to overrides.
Contains override classes to be used to change some settings in
transmute functions. Override scripts will set their own versions of this
object.
Also contains functions which are called to work through a series of known
rules to check the validity of applying a loop.
'''

from psytran.family import (
    string_match_ref_var,
    work_out_collapse_depth)


class TagOverride:
    '''
    Class to store combined metadata of an ignore list associated with a
    loop tag.
    This data will be provided by a global.py or file override which calls
    global. These will need to be found by user and manually added to this
    object in global.py or file override for the transmute method.
    '''
    def __init__(
                self,
                loop_tag,
                options=None
                ):
        '''
        Initialise TagOverride with a loop tag and an options list
        '''
        # Validation checks into class
        if options is None:
            options = {}
        if not isinstance(options, dict):
            raise TypeError(f"Expected a options dict, not \
                            '{type(options)}'.")

        self._loop_tag = loop_tag
        self._options = options

    # Getters
    def get_loop_tag(self):
        '''
        Return the loop tag of the class, name of the loop index.
        Name tag has been set by Loop.set_loop_type_inference_rules
        in the global script.
        '''
        return self._loop_tag

    def options(self):
        '''
        Return the options list of the class
        '''
        return self._options


class OverridesClass:
    '''
    Class to act as a full override for the global script.
    This will adjust settings used functions later on.
    This will contain a list of specific overrides for given loop tags.
    '''
    def __init__(self,
                 loop_max_qty=None,
                 tag_overrides=None
                 ):

        if tag_overrides is None:
            self._tag_overrides = []
        else:
            for override in tag_overrides:
                if not isinstance(override, TagOverride):
                    raise TypeError(f"Expected a tag_override object, not \
                                    '{type(override)}'.")
            # Pass through the list of accepted loop tag overrides
            self._tag_overrides = tag_overrides

        # setup default values for object properties
        self._loop_max_qty = 12

        # Override the defaults with provided values
        if loop_max_qty:
            self._loop_max_qty = loop_max_qty

    # Getters
    def get_loop_max_qty(self):
        '''
        Return the loop max value for number of loops that a parallel section
        will span over in span_parallel.
        '''
        return self._loop_max_qty

    def get_tag_overrides(self):
        '''
        A list of TagOverride objects. Set the loop_tag which the object is for
        and it's associated options list for the transformation.
        '''
        return self._tag_overrides


def validate_rules(loop_node, options):
    '''
    Function to store calls to all validations of loop.
    We can bundle them together with a result.
    '''

    valid_loop = False
    check_struct = False
    check_struct = string_match_ref_var(loop_node)

    if not check_struct:
        options = work_out_collapse_depth(loop_node, options)
        valid_loop = True

    return valid_loop, options
