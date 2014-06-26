import numpy as np
import os, glob
import json
import random, string
import re

import h5py
from nose.tools import raises, assert_in, assert_equal

from spikeylab.data.dataobjects import AcquisitionData, increment
from spikeylab.tools.exceptions import DataIndexError, DisallowedFilemodeError, \
                                        ReadOnlyError

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

def rand_id():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(4))

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

def test_increment_double_boundary():
    dimensions = (2,2,3,4)
    data_shape = (4,)
    current_index = [0,1,2,0]

    current_index = increment(current_index, dimensions, data_shape)
    assert current_index == [1,0,0,0]

def test_increment_single_middle_dim():
    dimensions = (2,1,4)
    data_shape = (4,)
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
    def tearDown(self):
        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            try:
                os.remove(f)
            except:
                pass

    def test_finite_dataset_append(self):
        """
        Test appending to the data structure when trace data has single
        dimension, e.g. (10,)
        """
        # such as for a tuning curve
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)

        np.testing.assert_array_equal(acq_data.get('fake/test_1', (1,)), fakedata*1)

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
        acq_data = self.setup_finite(fakedata, nsets)
        
        np.testing.assert_array_equal(acq_data.get('fake/test_1', (2,)), np.squeeze(fakedata*2))

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

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
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
        acq_data = self.setup_finite(fakedata, nsets, 'insert')

        np.testing.assert_array_equal(acq_data.get('fake/test_1', (1,)), fakedata*1)

        acq_data.close()

    def test_finite_dataset_single_point(self):

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = AcquisitionData(fname)

        acq_data.init_data('fake', (1,))
        acq_data.append('fake', [1])

        np.testing.assert_array_equal(acq_data.get('fake/test_1'), [1])

    def test_finite_dataset_save(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)
        acq_data.close()

        hfile = h5py.File(acq_data.filename)
        test = hfile['fake']['test_1']
        assert test.shape == (nsets, npoints)
        np.testing.assert_array_equal(test[1], fakedata*1)
        hfile.close()

    def test_finite_dataset_reload(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)
        acq_data.close()

        reloaded_acq_data = AcquisitionData(acq_data.filename, filemode='a')
        print 'hdf5 keys', reloaded_acq_data.hdf5.keys()

        reloaded_acq_data.init_data('fake1', (nsets, npoints))
        for iset in range(nsets):
            reloaded_acq_data.append('fake1', fakedata*iset)
        reloaded_acq_data.close()

        hfile = h5py.File(acq_data.filename)
        assert hfile.keys() == ['fake', 'fake1']
        hfile.close()

    def test_open_dataset_append_even_sets(self):
        """
        Test appending to, and consolidating dataset, ending in a 
        full temp set before consolidating.
        """
        nsets = 8
        npoints = 10
        fakedata = np.ones((npoints,))

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
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

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
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

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
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

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        print 'fname', fname
        acq_data = AcquisitionData(fname)
        acq_data.init_data('fake', (npoints,), mode='finite')

        attrs = {'sr': 500000, 'duration': 0.1, 'stimtype': 'tone', 'start_index':0, 'end_index':25}
        acq_data.append_trace_info('fake', attrs)
        acq_data.close()

        hfile = h5py.File(fname)
        test = hfile['fake']['test_1']
        stim = json.loads(test.attrs['stim'])
        assert_equal(stim[0]['duration'], 0.1)
        hfile.close()

    def test_continuous(self):
        nsets = 32
        npoints = 10000
        fakedata = np.ones((npoints,))

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = AcquisitionData(fname)
        acq_data.init_data('fake', mode='continuous')
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)

        acq_data.consolidate('fake')

        print 'sizes', acq_data.get('fake').size, nsets*npoints
        assert acq_data.get('fake').size == nsets*npoints
        acq_data.close()

        hfile = h5py.File(fname)
        test = hfile['fake']
        stim = json.loads(test.attrs['stim'])
        assert hfile['fake'].size == nsets*npoints
        assert hfile['fake'][0] == 0
        assert hfile['fake'][-1] == 31
        assert stim == []

        allsets = ''.join(hfile.keys())
        assert re.search('fake_set\d+', allsets) == None
        hfile.close()

    def test_continuous_with_stimattr(self):
        nsets = 32
        npoints = 10000
        fakedata = np.ones((npoints,))
        attrs = {'sr': 500000, 'duration': 0.1, 'stimtype': 'tone', 'start_time': 4.1}

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = AcquisitionData(fname)
        acq_data.init_data('fake', mode='continuous')
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)
            acq_data.append_trace_info('fake', attrs)

        acq_data.consolidate('fake')

        assert acq_data.get('fake').size == nsets*npoints
        acq_data.close()

        hfile = h5py.File(fname)
        test = hfile['fake']
        stim = json.loads(test.attrs['stim'])
        assert hfile['fake'].size == nsets*npoints
        assert hfile['fake'][0] == 0
        assert hfile['fake'][-1] == 31
        assert len(stim) == nsets
        hfile.close()

    def test_calibration_data(self):
        npoints = 250000
        caldata = np.ones((npoints,))
        calname ='calibration0'

        acq_data = self.setup_calibration(calname, caldata)
        acq_data.close_data(calname)
        cal1 = acq_data.get_calibration(calname, reffreq=15000)[0]

        # subtract one because vector gets shifted by reffreq value
        np.testing.assert_array_equal(caldata-1, cal1)
        assert acq_data.calibration_list() == [calname]
        acq_data.close()

    def test_reload_calibration_data(self):
        npoints = 250000
        caldata = np.ones((npoints,))
        calname ='calibration0'

        acq_data = self.setup_calibration(calname, caldata)
        acq_data.close()

        reloaded_acq_data = AcquisitionData(acq_data.filename, filemode='a')

        cal1 = reloaded_acq_data.get_calibration(calname, reffreq=15000)[0]

        # subtract one because vector gets shifted by reffreq value
        np.testing.assert_array_equal(caldata-1, cal1)
        assert reloaded_acq_data.calibration_list() == [calname]
        reloaded_acq_data.close()

    def test_nested_group(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))

        gname = 'outer/inner'
        acq_data = self.setup_finite(fakedata, nsets, groupname=gname)
        
        # auto naming of tests is regardless of group
        np.testing.assert_array_equal(acq_data.get(gname + '/test_1', (1,)), fakedata*1)
        acq_data.close()

        # make sure this is at the proper hierarchy in a raw HDF5 file
        hfile = h5py.File(acq_data.filename)
        assert hfile.keys() == ['outer']
        assert hfile['outer'].keys() == ['inner']
        assert hfile['outer']['inner']['test_1'].shape == (nsets, npoints)

        hfile.close()

        # test the AcquisitionData class's ability to reload nested groups
        reloaded_acq_data = AcquisitionData(acq_data.filename, filemode='r')
        reloaded_data = reloaded_acq_data.get(gname + '/test_1')
        assert reloaded_data.shape == (nsets, npoints)

    def test_read_only_data(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)
        acq_data.close()

        reloaded_acq_data = AcquisitionData(acq_data.filename, filemode='r')
        assert reloaded_acq_data.hdf5.keys() == ['fake']
        reloaded_data = reloaded_acq_data.get('fake/test_1')
        assert reloaded_data.shape == (nsets, npoints)

        reloaded_acq_data.close()

    @raises(ReadOnlyError)
    def test_read_only_write_error(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)
        acq_data.close()

        reloaded_acq_data = AcquisitionData(acq_data.filename, filemode='r')
        reloaded_acq_data.init_data('fake1', (nsets, npoints))

    @raises(DisallowedFilemodeError)
    def test_bad_filemode_error(self):
        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = AcquisitionData(fname, filemode='w+')

    def setup_calibration(self, calname, caldata):

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = AcquisitionData(fname)

        acq_data.init_group(calname, mode='calibration')
        acq_data.init_data(calname, mode='calibration', 
                            dims=caldata.shape, nested_name='calibration_intensities')
        acq_data.append(calname, caldata, nested_name='calibration_intensities')
        relevant_info = {'frequencies': 'all', 'calibration_dB':115,
                         'calibration_voltage': 1.0, 'calibration_frequency': 15000,
                         }
        acq_data.append_trace_info(calname, {'samplerate_da':100000})
        acq_data.set_metadata('/'.join([calname, 'calibration_intensities']),
                              relevant_info)

        return acq_data

    def setup_finite(self, fakedata, nsets, operation='append', groupname='fake'):
        # npoints = len(np.squeeze(fakedata))
        fakedata = np.array(fakedata)
        npoints = max(fakedata.shape)
        print 'len {} and shape {}'.format(len(fakedata), fakedata.shape)

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = AcquisitionData(fname)

        acq_data.init_data(groupname, (nsets, npoints))
        for iset in range(nsets):
            if operation == 'append':
                acq_data.append(groupname, fakedata*iset)
            else:
                acq_data.insert(groupname, [iset], fakedata*iset)

        return acq_data