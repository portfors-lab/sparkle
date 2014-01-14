import numpy as np
import os
import json

import h5py
from nose.tools import raises, assert_in, assert_equal

from spikeylab.data.dataobjects import AcquisitionData, increment
from spikeylab.tools.exceptions import DataIndexError

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

def test_increment_index_by_1():
    dimensions = (2,3,4)
    data_shape = (1,)
    current_index = [0,0,1]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [0,0,2]

def test_increment_index_single_low_dimension():
    dimensions = (2,3,4)
    data_shape = (4,)
    current_index = [0,1,0]

    increment(current_index, dimensions, data_shape)
    assert current_index == [0,2,0]

def test_increment_index_double_low_dimension():
    dimensions = (2,3,4)
    data_shape = (1,4,)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [0,1,0]

def test_increment_index_mid_dimension():
    dimensions = (2,3,4)
    data_shape = (2,4,)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [0,2,0]

def test_increment_index_high_dimension():
    dimensions = (2,3,4)
    data_shape = (1,3,4,)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [1,0,0]

@raises(DataIndexError)
def test_bad_data_shape():
    dimensions = (2,3,4)
    data_shape = (4,1)
    current_index = [0,0,0]

    current_index = increment(current_index, dimensions, data_shape)

class TestAcqusitionData():
    """
    Test creating, putting and getting to acquisition data structure
    """
    def test_finite_dataset_append(self):
        """
        Test appending to the data structure when trace data has single
        dimension, e.g. (10,)
        """
        # such as for a tuning curve
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))

        fname = os.path.join(tempfolder, 'savetemp.hdf5')
        acq_data = AcquisitionData(fname)
            
        acq_data.init_data('fake', (nsets, npoints))
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)

        np.testing.assert_array_equal(acq_data.get('test_0', (1,)), fakedata*1)

        acq_data.close()

    def test_finite_dataset_append_double_dimension(self):
        """
        Test appending to the data structure when trace data has double
        dimension, but still a vector e.g. (10,1)
        """
        # such as for a tuning curve
        nsets = 3
        npoints = 10
        fakedata = np.ones((1,npoints))

        fname = os.path.join(tempfolder, 'savetemp.hdf5')
        acq_data = AcquisitionData(fname)
            
        acq_data.init_data('fake', (nsets, npoints))
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)

        np.testing.assert_array_equal(acq_data.get('test_0', (2,)), np.squeeze(fakedata*2))

        acq_data.close()

    @raises(TypeError)
    def test_finite_dataset_append_error(self):
        """
        Test appending to the data structure when trace data incorrect
        dimension according to intialized dimensions
        """
        # such as for a tuning curve
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))

        fname = os.path.join(tempfolder, 'savetemp.hdf5')
        acq_data = AcquisitionData(fname)
            
        try:
            acq_data.init_data('fake', (nsets, nsets))
            for iset in range(nsets):
                acq_data.append('fake', fakedata*iset)

            np.testing.assert_array_equal(acq_data.get('fake', (2,)), fakedata*2)
        finally:
            acq_data.close()

    def test_finite_dataset_insert(self):
        # such as for a tuning curve -- not sure I am going to use this
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))

        fname = os.path.join(tempfolder, 'savetemp.hdf5')
        acq_data = AcquisitionData(fname)
            
        acq_data.init_data('fake', (nsets, npoints))
        for iset in range(nsets):
            acq_data.insert('fake', [iset], fakedata*iset)

        np.testing.assert_array_equal(acq_data.get('test_0', (1,)), fakedata*1)

        acq_data.close()

    def test_open_dataset_append_even_sets(self):
        """
        Test appending to, and consolidating dataset, ending in a 
        full temp set before consolidating.
        """
        nsets = 8
        npoints = 10
        fakedata = np.ones((npoints,))

        fname = os.path.join(tempfolder, 'savetemp.hdf5')
        acq_data = AcquisitionData(fname)
        acq_data.open_set_size = 4
            
        acq_data.init_data('fake', (npoints,), mode='open')
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)
        acq_data.trim('fake')

        np.testing.assert_array_equal(acq_data.get('fake', (6,)), fakedata*6)
        np.testing.assert_array_equal(acq_data.get('fake', (1,)), fakedata*1)
        acq_data.close()

    def test_open_dataset_append_mid_set(self):
        """
        Test appending to, and consolidating dataset, ending in a 
        partial temp set before consolidating.
        """
        nsets = 13
        npoints = 10
        fakedata = np.ones((npoints,))

        fname = os.path.join(tempfolder, 'savetemp.hdf5')
        acq_data = AcquisitionData(fname)
        acq_data.open_set_size = 4
        
        acq_data.init_data('fake', (npoints,), mode='open')
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)
        acq_data.trim('fake')

        np.testing.assert_array_equal(acq_data.get('fake', (8,)), fakedata*8)
        np.testing.assert_array_equal(acq_data.get('fake', (1,)), fakedata*1)
        acq_data.close()

    def test_adding_open_attrs(self):
        npoints = 10

        fname = os.path.join(tempfolder, 'savetemp.hdf5')
        acq_data = AcquisitionData(fname)
        acq_data.init_data('fake', (npoints,), mode='open')

        attrs = {'sr': 500000, 'duration': 0.1, 'stimtype': 'tone', 'start_index':0, 'end_index':25}
        acq_data.append_trace_info('fake', attrs)
        acq_data.close()

        hfile = h5py.File(fname)
        stim = json.loads(hfile['fake'].attrs['stim'])
        assert_equal(stim[0]['duration'], 0.1)
        hfile.close()


    def test_adding_finite_attrs(self):
        npoints = 10

        fname = os.path.join(tempfolder, 'savetemp.hdf5')
        acq_data = AcquisitionData(fname)
        acq_data.init_data('fake', (npoints,), mode='finite')

        attrs = {'sr': 500000, 'duration': 0.1, 'stimtype': 'tone', 'start_index':0, 'end_index':25}
        acq_data.append_trace_info('fake', attrs)
        acq_data.close()

        hfile = h5py.File(fname)
        test = hfile['fake']['test_0']
        stim = json.loads(test.attrs['stim'])
        assert_equal(stim[0]['duration'], 0.1)
        hfile.close()
