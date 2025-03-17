! (C) Crown Copyright 2023, Met Office. All rights reserved.
!
! This file is part of PSyTran and is released under the BSD 3-Clause license.
! See LICENSE in the root of the repository for full licensing details.

MODULE double_loop_mod

  IMPLICIT NONE

  CONTAINS

    SUBROUTINE double_loop(m, n, arr)
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: m
      INTEGER, INTENT(IN) :: n
      REAL, INTENT(OUT) :: arr(m,n)
      INTEGER :: i, j

      DO j = 1, n
        DO i = 1, m
          arr(i,j) = 0.0
        END DO
      END DO
    END SUBROUTINE double_loop

END MODULE double_loop_mod
