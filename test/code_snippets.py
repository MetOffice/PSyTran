# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
This module contains Fortran code snippets used for testing.
"""

# pylint: disable=C0103

loop_with_1_assignment = """
    PROGRAM test
      REAL :: a(10)
      INTEGER :: i

      DO i = 1, 10
        a(i) = 0.0
      END DO
    END PROGRAM test
    """

double_loop_with_1_assignment = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
      END DO
    END PROGRAM test
    """

triple_loop_with_1_assignment = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            a(i,j,k) = 0.0
          END DO
        END DO
      END DO
    END PROGRAM test
    """

quadruple_loop_with_1_assignment = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k
      INTEGER :: l

      DO l = 1, 10
        DO k = 1, 10
          DO j = 1, 10
            DO i = 1, 10
              a(i,j,k,l) = 0.0
            END DO
          END DO
        END DO
      END DO
    END PROGRAM test
    """

loop_with_1_assignment_and_intrinsic_call = """
    PROGRAM test
      REAL :: a(10)
      INTEGER :: i

      DO i = 1, 10
        a(i) = ABS(-i)
      END DO
    END PROGRAM test
    """

triple_loop_with_conditional_1_assignment = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            IF (i > 0) THEN
              a(i,j,k) = 0.0
            END IF
          END DO
        END DO
      END DO
    END PROGRAM test
    """

double_loop_with_2_loops = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
      END DO
    END PROGRAM test
    """

loop_with_3_assignments = """
    PROGRAM test
      REAL :: a(10)
      REAL :: b(10)
      INTEGER :: i

      DO i = 1, 10
        a(i) = 0.0
        b(i) = a(i)
        a(i) = 1.0
      END DO
    END PROGRAM test
    """

loop_with_2_literal_assignments = """
    PROGRAM test
      REAL :: a(10)
      REAL :: b(10)
      INTEGER :: i

      DO i = 1, 10
        a(i) = 0.0
        b(i) = 1.0
      END DO
    END PROGRAM test
    """

double_loop_with_3_assignments = """
    PROGRAM test
      REAL :: a(10,10)
      REAL :: b(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          a(i,j) = 0.0
          b(i,j) = a(i,j)
          a(i,j) = 1.0
        END DO
      END DO
    END PROGRAM test
    """

double_loop_with_conditional_3_assignments = """
    PROGRAM test
      REAL :: a(10,10)
      REAL :: b(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          IF (i > 0) THEN
            a(i,j) = 0.0
            b(i,j) = a(i,j)
            a(i,j) = 1.0
          END IF
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_double_loop_with_if = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        IF (j > 0) THEN
          DO i = 1, 10
            a(i,j) = 0.0
          END DO
        END IF
      END DO
    END PROGRAM test
    """

imperfectly_nested_double_loop_before = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        a(1,j) = 1.0
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_double_loop_after = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO j = 1, 10
        DO i = 1, 10
          a(i,j) = 0.0
        END DO
        a(1,j) = 1.0
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop1_with_if = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        IF (k > 0) THEN
          DO j = 1, 10
            DO i = 1, 10
              a(i,j,k) = 0.0
            END DO
          END DO
        END IF
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop1_before = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        a(1,1,k) = 1.0
        DO j = 1, 10
          DO i = 1, 10
            a(i,j,k) = 0.0
          END DO
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop1_after = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            a(i,j,k) = 0.0
          END DO
        END DO
        a(1,1,k) = 1.0
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop1_before_with_if = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        a(1,1,k) = 1.0
        DO j = 1, 10
          DO i = 1, 10
            IF (i > 0) THEN
              a(i,j,k) = 0.0
            END IF
          END DO
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop1_after_with_if = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            IF (i > 0) THEN
              a(i,j,k) = 0.0
            END IF
          END DO
        END DO
        a(1,1,k) = 1.0
      END DO
    END PROGRAM test
    """

conditional_imperfectly_nested_triple_loop1 = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        IF (k > 0) THEN
          DO j = 1, 10
            DO i = 1, 10
              a(i,j,k) = 0.0
            END DO
          END DO
        END IF
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop2_before = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          a(1,j,k) = 1.0
          DO i = 1, 10
            a(i,j,k) = 0.0
          END DO
        END DO
      END DO
    END PROGRAM test
    """

imperfectly_nested_triple_loop2_after = """
    PROGRAM test
      REAL :: a(10,10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO k = 1, 10
        DO j = 1, 10
          DO i = 1, 10
            a(i,j,k) = 0.0
          END DO
          a(1,j,k) = 1.0
        END DO
      END DO
    END PROGRAM test
    """

serial_loop = """
    PROGRAM test
      REAL :: a(10)
      INTEGER :: i

      a(1) = 0.0
      DO i = 2, 10
        a(i) = a(i-1)
      END DO
    END PROGRAM test
    """

dependent_double_loop = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j

      DO i = 1, 10
        DO j = i, 10
          a(i,j) = 0
        END DO
      END DO
    END PROGRAM test
    """

dependent_triple_loop = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO i = 1, 10
        DO j = i, 10
          DO k = 1, 10
            a(i,j,k) = 0
          END DO
        END DO
      END DO
    END PROGRAM test
    """

dependent_triple_subloop = """
    PROGRAM test
      REAL :: a(10,10)
      INTEGER :: i
      INTEGER :: j
      INTEGER :: k

      DO i = 1, 10
        DO j = 1, 10
          DO k = j, 10
            a(i,j,k) = 0
          END DO
        END DO
      END DO
    END PROGRAM test
    """

array_assignment_1d = """
    PROGRAM test
      REAL :: a(10)

      a(:) = 0.0
    END PROGRAM test
    """

array_assignment_2d = """
    PROGRAM test
      REAL :: a(10,10)

      a(:,:) = 0.0
    END PROGRAM test
    """

array_assignment_3d = """
    PROGRAM test
      REAL :: a(10,10,10)

      a(:,:,:) = 0.0
    END PROGRAM test
    """

implied_array_assignment_1d = """
    PROGRAM test
      REAL :: a(10)

      a = 0.0
    END PROGRAM test
    """

implied_array_assignment_2d = """
    PROGRAM test
      REAL :: a(10,10)

      a = 0.0
    END PROGRAM test
    """

implied_array_assignment_3d = """
    PROGRAM test
      REAL :: a(10,10,10)

      a = 0.0
    END PROGRAM test
    """

double_loop_with_index_array = """
  PROGRAM test
    INTEGER :: i, j, k
    INTEGER :: indices(10)
    REAL :: a(10,10)
    REAL :: b(10,10)

    DO j = 1, 10
      k = indices(j)
      DO i = 1, 10
        a(i,k) = a(i,k) + b(i,j) + b(i,j)
      END DO
    END DO
  END PROGRAM test
  """

subroutine_call = """
    PROGRAM test
      USE my_mod, ONLY: my_subroutine
      REAL :: a(10)

      CALL my_subroutine(a)
    END PROGRAM test
    """

# pylint: enable=C0103
