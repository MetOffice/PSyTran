##############################################################################
# Copyright (c) 2025,  Met Office, on behalf of HMSO and Queen's Printer
# For further details please refer to the file LICENCE.original which you
# should have received as part of this distribution.
##############################################################################

'''
Holds class with getter wrappers for global transformations which are
pre-configured. Intended to reduce duplication when defining transformations.
'''


from psyclone.transformations import (OMPLoopTrans, OMPParallelTrans)


class PropTrans:
    '''
    Class to store pre-configured transformations with getters
    '''
    def __init__(self):
        '''
        Initialise class with default properties
        '''

        # Setup transformations and their properties
        # OMP parallel do transformation
        self._omp_transform_par_do = OMPLoopTrans(
            omp_schedule="static",
            omp_directive="paralleldo")
        self._omp_parallel = OMPParallelTrans()
        self._omp_transform_do = OMPLoopTrans(
            omp_schedule="static",
            omp_directive="do")

    # Getters
    def omp_transform_par_do(self):

        '''
        Get pre configured omp_transform_par_do
        '''
        return self._omp_transform_par_do

    def omp_parallel(self):

        '''
        Get pre configured omp_parallel
        '''
        return self._omp_parallel

    def omp_transform_do(self):

        '''
        Get pre configured omp_transform_do
        '''
        return self._omp_transform_do
