# ..
#    (C) Crown Copyright, Met Office. All rights reserved.
#
#    This file is part of PSyACC and is released under the BSD 3-Clause
#    license. See LICENSE in the root of the repository for full licensing
#    details.
#
#
# Demo 2: Inserting OpenACC ``kernels`` directives using PSyACC
# =============================================================
#
# The `previous demo <01_psyclone.py.html>`__ showed how to run PSyclone in
# code transformation mode from the command line, albeit with a trivial
# transformation function. Here, we use a more interesting transformation
# function, which makes use of PSyACC.
#
# We also consider a slightly more interesting snippet of Fortran source, as
# given in ``fortran/single_loop.py``:
#
# .. literalinclude:: fortran/single_loop.F90
#    :language: fortran
#    :lines: 6-
#
# That is, we have a subroutine involving a loop over an array of floating
# point numbers and just set each entry to zero.
#
# In this case, the recommended command is
#
# .. literalinclude:: 02_kernels.sh
#    :language: bash
#    :lines: 8-
#
# We begin by importing from the namespace PSyACC, as well as the ``nodes``
# module of PSyclone. ::

from psyacc import *
from psyclone.psyir import nodes

# Recall that the main thing that PSyclone will take from this file is the
# ``trans`` function. For demonstration purposes, we decompose it into
# subfunctions rather than writing out the final result all at once. In each
# case, follow the signature of ``trans`` so that the subfunction takes the
# :py:class:`psyclone.psyGen.PSy` instance ``psy`` as an argument and returns
# it, with or without modification.
#
# First, let's count how many invokes are associated with ``psy``. ::


def count_invokes(psy):
    num_invokes = len(psy.invokes.invoke_list)
    print(f"Number of invokes: {num_invokes}")
    return psy


# The result should be
#
# .. code-block::
#
#    Number of invokes: 1
#
# because our Fortran script is a program with no other modules or procedures.
#
# Next, we view the schedule for the invoke. ::


def view_schedule(psy):
    schedule = psy.invokes.invoke_list[0].schedule
    print(
        f"""
Schedule
~~~~~~~~

{schedule}"""
    )
    return psy


# .. code-block:: bash
#
#    Schedule
#    ~~~~~~~~
#
#    NemoInvokeSchedule:
#    NemoLoop[variable:'i', loop_type:'unknown']
#    Literal[value:'1', Scalar<INTEGER, UNDEFINED>]
#    Reference[name:'n']
#    Literal[value:'1', Scalar<INTEGER, UNDEFINED>]
#    Schedule:
#    Assignment[]
#    ArrayReference[name:'arr']
#    Reference[name:'i']
#    Literal[value:'0.0', Scalar<REAL, UNDEFINED>]
#    End Schedule
#    End NemoLoop
#    End NemoInvokeSchedule
#
# Now for the more interesting bit: let's use PSyACC to add some OpenACC
# syntax. To do this, we need to find the loop within the schedule. This can be
# achieved using the ``walk`` method of PSyclone's
# :py:class:`psyclone.psyir.nodes.node.Node` class. Before taking the first
# loop found, we check that it was the only one.
#
# Having found the loop, we can apply an OpenACC ``kernels`` directive to it
# using PSyACC's :py:func:`psyacc.directives.apply_kernels_directive`. The
# effect of this will be to instruct the NVHPC Fortran compiler to run the
# loop on the GPU. Since we do not provide any other instructions, the
# compiler is free to optimise the GPU configuration for the GPU device
# however it sees fit.
#
# .. note::
#
#    The key difference between the ``kernels`` and ``parallel`` directives
#    is that with the former the compiler will apply all clauses explicitly
#    mentioned in the code, plus any others it sees fit, whereas with the
#    latter it will only use the clauses provided. That is, ``parallel`` gives
#    more control to the user whereas ``kernels`` gives more freedom to the
#    compiler.
#
# ::


def apply_openacc_kernels(psy):
    schedule = psy.invokes.invoke_list[0].schedule

    # Get the (only) loop
    loops = schedule.walk(nodes.Loop)
    assert len(loops) == 1
    loop = loops[0]

    # Insert OpenACC syntax
    apply_kernels_directive(loop)

    # View the modified schedule
    print(
        f"""
Modified schedule
~~~~~~~~~~~~~~~~~

{schedule}"""
    )
    return psy


# As shown below, the schedule for the main program has now been modified to
# use OpenACC syntax: there is a
# :py:class:`psyclone.psyir.nodes.acc_directives.ACCKernelsDirective`, which
# hides the original schedule within it.
#
# .. code-block:: bash
#
#    Modified schedule
#    ~~~~~~~~~~~~~~~~~
#
#    NemoInvokeSchedule:
#    ACCKernelsDirective[]
#    End NemoInvokeSchedule
#
# Finally, we bring all of the above together by combining them in the
# ``trans`` function which will be picked up by PSyclone. ::


def trans(psy):
    return apply_openacc_kernels(view_schedule(count_invokes(psy)))


# Running the PSyclone command given at the beginning of this demo should
# generate the output ``02_kernels-single_loop.F90`` with contents as follows:
#
# .. literalinclude:: outputs/02_kernels-single_loop.F90
#    :language: fortran
#
# Again, the source code has clearly been reformatted to use lower case and
# increased spacing. (A few other reformattings are left as a
# spot-the-difference exercise!) The main thing to note, though, is that an
# OpenACC ``kernels`` directive has indeed been applied to the loop.
#
# Let's check that we are able to compile the PSyclone-generated program.
# First, load a working NVHPC installation. Usually, this is achieved with
# commands of the form
#
# .. code-block::
#
#    module use path/to/nvhpc/modulefiles
#    module load nvhpc/XX.Y
#
# where ``path/to/nvhpc/modulefiles`` should be replaced by the path to the
# modulefile for the NVHPC installation and ``XX.Y`` should be replaced with
# the version to be loaded.
#
# .. note::
#    For internal Met Office users, the instructions on
#    `this page <https://metoffice.sharepoint.com/sites/MetOfficeSSECommunity/SitePages/OpenACC-GPU-Porting.aspx>`__
#    may be of use. If you are using Isambard then see the instructions in the
#    Compilation section of the
#    `MACS page <https://metoffice.sharepoint.com/sites/MetOfficeSSECommunity/SitePages/GPU-Isambard-MACS.aspx#compilation>`__
#    and/or the
#    `Phase-3 page <https://metoffice.sharepoint.com/sites/MetOfficeSSECommunity/SitePages/GPU-Isambard-Phase3.aspx#compilation>`__.
#
#
# Loading an NVHPC installation as above will put an ``nvfortran`` binary in
# your path. Compile the generated Fortran file with
#
# .. code-block:: bash
#
#    nvfortran -c -acc=gpu -Minfo=accel outputs/02_kernels-single_loop.F90
#
# Here, we instruct the compiler to target the accelerator type 'GPU'. This
# will enable OpenACC syntax. The additional ``-Minfo=accel`` flag tells the
# compiler to print information related to the accelerator. You should see
# compiler output
#
# .. code-block::
#
#    single_loop:
#         11, Generating implicit copyout(arr(:n)) [if not already present]
#         12, Loop is parallelizable
#             Generating NVIDIA GPU code
#             12, !$acc loop gang, vector(128) ! blockidx%x threadidx%x
#
# From this, we may deduce a few things.
#
# * The loop on line 12 is deemed to be parallelisable.
# * The compiler opts to parallelise this loop using both gang and vector
#   parallelism, with a vector length of 128.
# * OpenACC's *managed memory* functionality is being used by default. As
#   such, the compiler determines that a GPU-to-CPU data transfer is required
#   to copy the array ``arr`` (which has ``intent(out)``) out of the
#   subroutine. This is indicated by the use of an implicit use of the OpenACC
#   data directive clause ``copyout``.
#
# In the `next demo <03_loop.py.html>`__ we'll build on this and additionally
# apply an OpenACC ``loop`` directive, with appropriate clauses.
#
# This demo can also be viewed as a `Python script <02_kernels.py>`__.
