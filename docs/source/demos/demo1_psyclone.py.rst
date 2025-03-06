..
   (C) Crown Copyright 2023, Met Office. All rights reserved.

   This file is part of PSyACC and is released under the BSD 3-Clause
   license. See LICENSE in the root of the repository for full licensing
   details.

.. # pylint: disable=C0114
.. # pylint: disable=C0116


Demo 1: PSyclone transformations from the command line
======================================================

Here we demonstrate how to run PSyclone in code transformation mode from the
command line. Despite being in 'transformation mode', we won't actually apply
any code transformations in this demo. We'll simply read some Fortran source
code and then write it out to a different file.

.. warning::
   The first, important thing to note is that these demos are not intended to
   be run directly.

Instead of running the demos as Python scripts, they should be passed as
transformation scripts for the ``psyclone`` command. This command will only
be available if you have installed PSyclone and have activated the virtual
environment you used when installing it (and PSyACC).

The recommended command for this demo is as follows.

.. literalinclude:: demo1_psyclone.sh
   :language: bash
   :lines: 9-

There is a lot to unpack here! Let's work through the arguments one by one.

API
---

PSyclone requires an API to be chosen, i.e., the argument following ``-api``.
Since PSyACC is designed to use the NEMO API, we should always choose this.

Source code
-----------

Perhaps the most important argument is the source code to be transformed (the
last argument). We provide a subdirectory of Fortran source to be used for
this purpose. In this demo, we parse the ``empty.F90`` file, which contains a
'Hello, World!' Fortran program:

.. literalinclude:: fortran/empty.F90
   :language: fortran
   :lines: 6-

Transformation script
---------------------

The ``-s`` option is used to provide a transformation script to
PSyclone. In this case, we pass this file. Given that almost all of it is
comprised of comments, the only Python syntax that will be picked up is the
following. ::


  def trans(psy):
      print("Hello, PSyACC World!")
      return psy


The transformation function *must* have the name ``trans``, *must* have a
single argument (the :py:class:`psyclone.psyGen.PSy` instance), and *must*
return the same :py:class:`psyclone.psyGen.PSy` instance, usually modified in
some way. In this demo, we don't actually make any modifications and instead
just say hello to the user.

Output file
-----------

Finally, we need to tell PSyclone where to write the transformed code to. If
this argument is dropped then the transformed code will be printed to screen.
We pass the location ``outputs/demo1_psyclone-empty.F90`` as a combination of
the names of the source file and transformation script. The ``output``
subdirectory should have been created when you installed PSyACC.

Inspecting the output file, it should look something like.

.. literalinclude:: outputs/demo1_psyclone-empty.F90
   :language: fortran

It doesn't take a Fortran expert to realise that running the two versions of
the Fortran code will give the same result. However, the files themselves are
slightly different, even though the transformation function that we used was
trivial. The reason for this is that PSyclone always reformats code according
to its in-built preferences. In particular, it will use lower case (for the
most part) and will put a single blank line at the start and end of any
program.

In the `next demo <demo2_kernels.py.html>`__, we'll develop a more
interesting transformation script, which uses PSyACC to apply an OpenACC
``kernels`` directive to a simple loop.

This demo can also be viewed as a `Python script <demo1_psyclone.py>`__.

.. # pylint: enable=C0114
.. # pylint: enable=C0116
