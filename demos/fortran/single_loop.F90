! (C) Crown Copyright 2023, Met Office. All rights reserved.
!
! This file is part of PSyTran and is released under the BSD 3-Clause license.
! See LICENSE in the root of the repository for full licensing details.

MODULE single_loop_mod

  CONTAINS

    SUBROUTINE single_loop(n, arr)
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: n
      REAL, INTENT(OUT) :: arr(n)
      INTEGER :: i

      DO i = 1, n
        arr(i) = 0.0
      END DO
    END SUBROUTINE single_loop

END MODULE single_loop_mod
