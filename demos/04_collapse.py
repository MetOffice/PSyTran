# ..
#    (C) Crown Copyright, Met Office. All rights reserved.
#
#    This file is part of PSyACC and is released under the BSD 3-Clause
#    license. See LICENSE in the root of the repository for full licensing
#    details.
#
#
# Demo 4: Applying OpenACC ``collapse`` clauses using PSyACC
# ==========================================================
#
# The `previous demo <03_loop.py.html>`__ showed how to insert OpenACC ``loop``
# directives with ``gang``, ``vector``, and ``seq`` clauses into Fortran code
# using PSyACC. In this demo, we consider the ``collapse`` clause, which can be
# used to combine loops whose iterations are independent of one another, to
# increase data throughput.
#
# Consider again the same double loop example:
#
# .. literalinclude:: fortran/double_loop.F90
#    :language: fortran
#    :lines: 6-
#
# Convince yourself that combining the ``j`` and ``i`` loops as follows would
# have the same result.
#
# .. code-block:: fortran
#
#      mn = m * n
#      DO k = 1, mn
#        i = MOD(mn,m)
#        j = (k - i) / m
#        arr(i,j) = 0.0
#      END DO
#
# This is effectively what the OpenACC ``collapse`` clause does.
#
# The PSyclone command for this demo is as follows.
#
# .. literalinclude:: 04_collapse.sh
#    :language: bash
#    :lines: 8-
#
# Again, begin by importing from the namespace PSyACC, as well as the ``nodes``
# module of PSyclone. ::

from psyacc import *
from psyclone.psyir import nodes

# In the demos so far, we have built up transformation scripts piece by piece.
# This was done for demonstration purposes; in many cases, it is easier to
# just write it out at once. In the following ``trans`` script, you will
# recognise many of the elements from the previous demos. The difference is the
# call to :func:`psyacc.clauses.apply_loop_collapse`, which takes a second
# argument ``collapse``. This is the number of loops within the nest that
# should be collapsed together, starting from the loop that it is being applied
# to. ::


def trans(psy):
    schedule = psy.invokes.invoke_list[0].schedule

    # Get the outer-most loop
    loops = schedule.walk(nodes.Loop)
    outer_loops = list(filter(is_outer_loop, loops))
    assert len(outer_loops) == 1
    outer_loop = outer_loops[0]

    # Insert OpenACC syntax
    apply_kernels_directive(outer_loop)
    apply_loop_collapse(outer_loop, collapse=2)
    return psy


# Running this example using the PSyclone command above, you should find that
# the output in ``outputs/04_collapse-double_loop.F90`` reads as follows.
#
# .. literalinclude:: outputs/04_collapse-double_loop.F90
#    :language: fortran
#
# Exercises
# ---------
#
# 1. Following the same approach as in the previous demos, check that you can
#    compile the PSyclone-generated Fortran file. Does the compiler output look
#    reasonable?
#
# 2. Recall the exercise in the `previous demo <03_loop.py.html>`__ where we
#    applied the transformation script to ``single_loop.F90``, as opposed to
#    ``double_loop.F90``. What happens when we do that in this case?
#
# 3. What happens when the ``collapse`` argument is removed from the call to
#    :func:`psyacc.clauses.apply_loop_collapse` in the transformation script?
#    Is the output the same? Convince yourself that everything is working as
#    expected by reading the `API documentation <../psyacc.html>`__.
#
# This demo can also be viewed as a `Python script <04_collapse.py>`__.
