# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
Module for setting up Pytest fixtures.
"""
import pytest

# pylint: disable=W0611
from psyclone.tests.conftest import fixture_fortran_reader
from psyclone.transformations import ACCLoopTrans, OMPLoopTrans

# pylint: enable=W0611


@pytest.fixture(
    name="directive", params=[ACCLoopTrans, OMPLoopTrans], scope="module"
)
def fixture_directive(request):
    """Pytest fixture for loop transformations."""
    return request.param()


@pytest.fixture(
    name="clause",
    params=["sequential", "gang", "vector", "collapse"],
    scope="module",
)
def fixture_clause(request):
    """Pytest fixture for loop clause."""
    return request.param


@pytest.fixture(name="collapse", params=[2, 3], scope="module")
def fixture_collapse(request):
    """Pytest fixture for number of loops to collapse."""
    return request.param


@pytest.fixture(name="dim", params=[1, 2, 3], scope="module")
def fixture_dim(request):
    """Pytest fixture for spatial dimension."""
    return request.param


@pytest.fixture(
    name="imperfection", params=["before", "after", "if"], scope="module"
)
def fixture_imperfection(request):
    """
    Pytest fixture determining whether a loop nest imperfection comes before
    or after a loop.
    """
    return request.param


@pytest.fixture(name="inclusive", params=[True, False], scope="module")
def fixture_inclusive(request):
    """
    Pytest fixture to control whether the current node is included in
    searches.
    """
    return request.param


@pytest.fixture(name="nest_depth", params=[1, 2, 3, 4], scope="module")
def fixture_nest_depth(request):
    """Pytest fixture for depth of a loop nest."""
    return request.param


@pytest.fixture(
    name="omp_directive",
    params=[
        "do",
        "loop",
        "paralleldo",
        "teamsloop",
        "teamsdistributeparalleldo",
    ],
    scope="module",
)
def fixture_omp_directive(request):
    """Pytest fixture for omp directive parameter of OMPLoopTrans"""
    return request.param


@pytest.fixture(
    name="perfection", params=["1_assign", "3_assigns", "if"], scope="module"
)
def fixture_perfection(request):
    """Pytest fixture for code found within a perfectly nested loop."""
    return request.param


@pytest.fixture(
    name="relative", params=["ancestor", "descendent"], scope="module"
)
def fixture_relative(request):
    """Pytest fixture for the type of relative."""
    return request.param
