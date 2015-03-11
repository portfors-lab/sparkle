
from neurosound.data.hdf5data import HDF5Data
from neurosound.data.batlabdata import BatlabData

import test.sample as sample

class TestBatlabData():
    def setup(self):
        self.datafile = BatlabData(sample.batlabfile())

    def teardown(self):
        self.datafile.close()

    def test_load_batlab(self):
        # check some things we know about the data
        all_tests = self.datafile.all_datasets()
        assert len(all_tests) == 55

    def test_keys(self):
        datakeys = self.datafile.keys()

        assert len(datakeys) == 55
        assert 'test_1' in datakeys
        assert 'test_55' in datakeys

    def test_get_info(self):

        info = self.datafile.get_info('test_1')
        assert info['testtype'] == "General Auto Test"
        assert info['samplerate_ad'] == 40000

        info = self.datafile.get_info('test_8')
        assert info['testtype'] == "Tuning Curve"
        assert info['samplerate_ad'] == 40000

    def test_get_data(self):
        # test a few different shapes
        data = self.datafile.get_data('test_1')
        print 'data shape', data.shape
        assert data.shape == (8, 50, 8000)

        data = self.datafile.get_data('test_6')
        assert data.shape == (1, 200, 8000)

        data = self.datafile.get_data('test_55')
        assert data.shape == (68, 20, 8000)

    def test_get_trace_info(self):
        stim = self.datafile.get_trace_info('test_1')
        assert len(stim) == 8
        assert stim[0]['samplerate_da'] == 333333
        assert len(stim[0]['components']) == 0
        assert len(stim[1]['components']) == 2
        assert stim[1]['components'][1]['stim_type'] == "Vocalization"
        assert stim[1]['components'][1]['filename'] == "LowF2_harmonics_1-16.call1"

        stim = self.datafile.get_trace_info('test_6')
        assert len(stim) == 1
        assert stim[0]['samplerate_da'] == 333333
        assert len(stim[0]['components']) == 2
        assert stim[0]['components'][1]['stim_type'] == "Pure Tone"
        assert stim[0]['components'][1]['frequency'] == 14000