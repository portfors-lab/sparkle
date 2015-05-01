import glob
import json
import os
import random
import re
import string

import h5py
import numpy as np
from nose.tools import assert_equal, assert_in, raises

from sparkle.data.hdf5data import HDF5Data, recover_data_from_backup, autosave_filenames
from sparkle.tools.exceptions import DataIndexError, DisallowedFilemodeError, \
    OverwriteFileError, ReadOnlyError

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

def rand_id():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(4))

class TestHDF5Data():
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

    def test_open_without_ext(self):
        """
        Test that file is created with the exact name specified
        """
        fname = os.path.join(tempfolder, 'savetemp'+rand_id())
        acq_data = HDF5Data(fname)

        acq_data.init_data('fake', (1,))
        acq_data.append('fake', [1])

        print 'filename', acq_data.filename
        acq_data.close()

        assert os.path.isfile(fname)

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

        np.testing.assert_array_equal(acq_data.get_data('fake/test_1', (1,)), fakedata*1)

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
        
        np.testing.assert_array_equal(acq_data.get_data('fake/test_1', (2,)), np.squeeze(fakedata*2))

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
        acq_data = HDF5Data(fname)
            
        try:
            acq_data.init_data('fake', (nsets, npoints-1))
            for iset in range(nsets):
                acq_data.append('fake', fakedata*iset)

            np.testing.assert_array_equal(acq_data.get_data('fake', (2,)), fakedata*2)
        finally:
            acq_data.close()
            
    @raises(ValueError)
    def test_finite_append_overflow_error(self):
        """
        Test that an attempt to append more data than the dataset 
        initialized throws an error
        """
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = HDF5Data(fname)
            
        try:
            acq_data.init_data('fake', (nsets, npoints))
            for iset in range(nsets+1):
                acq_data.append('fake', fakedata*iset)

            np.testing.assert_array_equal(acq_data.get_data('fake', (2,)), fakedata*2)
        finally:
            acq_data.close()

    def test_finite_dataset_insert(self):
        # such as for a tuning curve -- not sure I am going to use this
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets, 'insert')

        np.testing.assert_array_equal(acq_data.get_data('fake/test_1', (1,)), fakedata*1)

        acq_data.close()

    def test_finite_dataset_single_point(self):

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = HDF5Data(fname)

        acq_data.init_data('fake', (1,))
        acq_data.append('fake', [1])

        np.testing.assert_array_equal(acq_data.get_data('fake/test_1'), [1])

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

        reloaded_acq_data = HDF5Data(acq_data.filename, filemode='a')
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
        acq_data = HDF5Data(fname)
        acq_data.open_set_size = 4
            
        acq_data.init_data('fake', (npoints,), mode='open')
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)
        acq_data.trim('fake')

        np.testing.assert_array_equal(acq_data.get_data('fake', (6,)), fakedata*6)
        np.testing.assert_array_equal(acq_data.get_data('fake', (1,)), fakedata*1)
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
        acq_data = HDF5Data(fname)
        acq_data.open_set_size = 4
        
        acq_data.init_data('fake', (npoints,), mode='open')
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)
        acq_data.trim('fake')

        np.testing.assert_array_equal(acq_data.get_data('fake', (8,)), fakedata*8)
        np.testing.assert_array_equal(acq_data.get_data('fake', (1,)), fakedata*1)
        acq_data.close()

    def test_adding_open_attrs(self):
        npoints = 10

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = HDF5Data(fname)
        acq_data.init_data('fake', (npoints,), mode='open')

        attrs = {'fs': 500000, 'duration': 0.1, 'stimtype': 'tone', 'start_index':0, 'end_index':25}
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
        acq_data = HDF5Data(fname)
        acq_data.init_data('fake', (npoints,), mode='finite')

        attrs = {'fs': 500000, 'duration': 0.1, 'stimtype': 'tone', 'start_index':0, 'end_index':25}
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
        acq_data = HDF5Data(fname)
        acq_data.init_data('fake', mode='continuous')
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)

        acq_data.consolidate('fake')

        print 'sizes', acq_data.get_data('fake').size, nsets*npoints
        assert acq_data.get_data('fake').size == nsets*npoints
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
        attrs = {'fs': 500000, 'duration': 0.1, 'stimtype': 'tone', 'start_time': 4.1}

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = HDF5Data(fname)
        acq_data.init_data('fake', mode='continuous')
        for iset in range(nsets):
            acq_data.append('fake', fakedata*iset)
            acq_data.append_trace_info('fake', attrs)

        acq_data.consolidate('fake')

        assert acq_data.get_data('fake').size == nsets*npoints
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

        reloaded_acq_data = HDF5Data(acq_data.filename, filemode='a')

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
        np.testing.assert_array_equal(acq_data.get_data(gname + '/test_1', (1,)), fakedata*1)
        acq_data.close()

        # make sure this is at the proper hierarchy in a raw HDF5 file
        hfile = h5py.File(acq_data.filename)
        assert hfile.keys() == ['outer']
        assert hfile['outer'].keys() == ['inner']
        assert hfile['outer']['inner']['test_1'].shape == (nsets, npoints)

        hfile.close()

        # test the HDF5Data class's ability to reload nested groups
        reloaded_acq_data = HDF5Data(acq_data.filename, filemode='r')
        reloaded_data = reloaded_acq_data.get_data(gname + '/test_1')
        assert reloaded_data.shape == (nsets, npoints)

    def test_read_only_data(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)
        acq_data.close()

        reloaded_acq_data = HDF5Data(acq_data.filename, filemode='r')
        assert reloaded_acq_data.hdf5.keys() == ['fake']
        reloaded_data = reloaded_acq_data.get_data('fake/test_1')
        assert reloaded_data.shape == (nsets, npoints)

        reloaded_acq_data.close()

    def test_empty_data_file_deleted(self):
        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = HDF5Data(fname)
        acq_data.close()

        assert not os.path.isfile(fname)

    @raises(ReadOnlyError)
    def test_read_only_write_error(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)
        acq_data.close()

        reloaded_acq_data = HDF5Data(acq_data.filename, filemode='r')
        reloaded_acq_data.init_data('fake1', (nsets, npoints))

    @raises(DisallowedFilemodeError)
    def test_bad_filemode_error(self):
        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = HDF5Data(fname, filemode='w+')

    @raises(OverwriteFileError)
    def test_overwrite_error(self):
        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = HDF5Data(fname)
        acq_data.init_data('fake1', (1, 2))
        acq_data.close()

        HDF5Data(fname, filemode='w-')

    def test_data_backup(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)

        # add another group to make sure we have multiple backup files we are collecting
        acq_data.init_data('segment0', (nsets, npoints))
        acq_data.set_metadata('segment0', {'raindrops': 'roses', 'whiskers':'kittens'})
        # data is only backed up when it is filled so...
        for iset in range(nsets):
            acq_data.append('segment0', fakedata)
        acq_data.backup('segment0')


        # add another segments with > 10 tests:
        for itest in range(12):
            acq_data.init_data('segment1', (nsets, npoints))
            # data is only backed up when it is filled so add data
            acq_data.set_metadata('segment1', {'just': 'dont', 'crash':'!!!!!'})
            for iset in range(nsets):
                acq_data.append('segment1', fakedata)
        acq_data.backup('segment1')

        original_set_names = acq_data.dataset_names()
        original_filename =  acq_data.hdf5.filename

        self.recover_and_check(acq_data)

    def test_data_backup_from_appended_file(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)

        # add another group to make sure we have multiple backup files we are collecting
        acq_data.init_data('segment0', (nsets, npoints))
        # data is only backed up when it is filled so...
        for iset in range(nsets):
            acq_data.append('segment0', fakedata)
        acq_data.backup('segment0')

        # close this data object normally, existing back up files should get cleaned up
        original_filename =  acq_data.hdf5.filename
        acq_data.close()

        # reopen - a backup should be made on open including all existing sets
        acq_data = HDF5Data(original_filename, filemode='a')

        # lets add another data set too
        acq_data.init_data('segment1', (nsets, npoints))
        for iset in range(nsets):
            acq_data.append('segment1', fakedata)
        acq_data.backup('segment1')

        # have two tests under the same segment
        acq_data.init_data('segment1', (nsets, npoints))
        for iset in range(nsets):
            acq_data.append('segment1', fakedata)
        acq_data.backup('segment1')

        original_set_names = acq_data.dataset_names()

        self.recover_and_check(acq_data)

    def recover_and_check(self, acq_data):
        original_set_names = acq_data.dataset_names()
        original_filename =  acq_data.hdf5.filename

        # if AcquisitionData object is closed normally, it will clean up the
        # backup files, so close the HDF5 file ourselves to by-pass this
        acq_data.hdf5.close()

        # recover from backups and compare to original
        backup_dir, backup_filename, prev_backups = autosave_filenames(original_filename)
        recovered_data = recover_data_from_backup(original_filename, prev_backups)

        # close this so we can re-open it as an HDF5Data object
        recovered_data.close()

        # recover_data_from_backup moves filenames around!
        # also since we still have the backup data present loading and HDF5 data object
        # will cause it to try to recover all over again... so delete the backup pieces
        for backup_file in prev_backups:
            os.remove(backup_file)

        # in recovered data, files get re-named
        recovered_acqdata = HDF5Data(original_filename, filemode='r')
        base_fname, ext = os.path.splitext(original_filename)
        original_acqdata = HDF5Data(base_fname+'_compromised0'+ext, filemode='r')

        # now check that all the data is the same
        assert recovered_acqdata.dataset_names() == original_acqdata.dataset_names() == original_set_names

        # check attrs got copied over
        assert_attrs_equal(original_acqdata.hdf5, recovered_acqdata.hdf5)
        
        recovered_acqdata.close()
        original_acqdata.close()

    def test_recover_from_constructor(self):
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)

        # add another group to make sure we have multiple backup files we are collecting
        acq_data.init_data('segment0', (nsets, npoints))
        # data is only backed up when it is filled so...
        for iset in range(nsets):
            acq_data.append('segment0', fakedata)

        acq_data.init_data('segment0', (nsets, npoints))
        for iset in range(nsets):
            acq_data.append('segment0', fakedata)
        acq_data.backup('segment0')

        original_set_names = acq_data.dataset_names()
        original_filename =  acq_data.hdf5.filename
        # if AcquisitionData object is closed normally, it will clean up the
        # backup files, so close the HDF5 file ourselves to by-pass this
        acq_data.hdf5.close()

        recovered_acqdata = HDF5Data(original_filename, filemode='r')
        # recovering the data will move the original file to _compromised
        base_fname, ext = os.path.splitext(original_filename)
        original_acqdata = HDF5Data(base_fname+'_compromised0'+ext, filemode='r')

        # now check that all the data is the same
        assert recovered_acqdata.dataset_names() == original_acqdata.dataset_names() == original_set_names

        # check attrs got copied over
        assert_attrs_equal(original_acqdata.hdf5, recovered_acqdata.hdf5)

        recovered_acqdata.close()
        original_acqdata.close()

    def test_data_apocalyse(self):
        # multiple crashes on same file
        nsets = 3
        npoints = 10
        fakedata = np.ones((npoints,))
        acq_data = self.setup_finite(fakedata, nsets)

        # add another group to make sure we have multiple backup files we are collecting
        acq_data.init_data('segment0', (nsets, npoints))
        # data is only backed up when it is filled so...
        for iset in range(nsets):
            acq_data.append('segment0', fakedata)

        acq_data.init_data('segment0', (nsets, npoints))
        for iset in range(nsets):
            acq_data.append('segment0', fakedata)
        acq_data.backup('segment0')

        original_set_names = acq_data.dataset_names()
        original_filename =  acq_data.hdf5.filename

        for crash_num in range(12):
            # if AcquisitionData object is closed normally, it will clean up the
            # backup files, so close the HDF5 file ourselves to by-pass this
            acq_data.hdf5.close()
            acq_data = HDF5Data(original_filename, filemode='a')
            print acq_data.dataset_names(), original_set_names
            assert acq_data.dataset_names() == original_set_names

        acq_data.close()

    def setup_calibration(self, calname, caldata):

        fname = os.path.join(tempfolder, 'savetemp'+rand_id()+'.hdf5')
        acq_data = HDF5Data(fname)

        acq_data.init_group(calname, mode='calibration')
        acq_data.init_data(calname, mode='calibration', 
                            dims=caldata.shape, nested_name='calibration_intensities')
        acq_data.init_data(calname, mode='calibration', dims=caldata.shape)
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
        acq_data = HDF5Data(fname)

        acq_data.init_data(groupname, (nsets, npoints))
        for iset in range(nsets):
            if operation == 'append':
                acq_data.append(groupname, fakedata*iset)
            else:
                acq_data.insert(groupname, [iset], fakedata*iset)

        acq_data.backup(groupname)
        return acq_data

# def assert_attrs_equal(original_acqdata, recovered_acqdata):
#     recovered_attrs = recovered_acqdata.get_info('')
#     for attr, val in original_acqdata.get_info('').items():
#         assert attr in recovered_attrs
#         assert recovered_attrs[attr] == val

#     # check group attrs
#     for key in original_acqdata.keys():
#         recovered_attrs = recovered_acqdata.get_info(key)
#         for attr, val in original_acqdata.get_info(key).items():
#             assert attr in recovered_attrs
#             print 'attr', attr, recovered_attrs[attr], val, type(val)
#             assert recovered_attrs[attr] == val

def assert_attrs_equal(ref_group, compare_group):
    for attr in ref_group.attrs:
        # print 'attr0:', ref_group.attrs[attr]
        # print 'attr1', compare_group.attrs[attr]
        assert ref_group.attrs[attr] == compare_group.attrs[attr]
    if hasattr(ref_group, 'keys'):
        for key in ref_group.keys():
            assert_attrs_equal(ref_group[key], compare_group[key])
