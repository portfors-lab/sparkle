
import test.sample as sample
from sparkle.data.batlabdata import BatlabData
from sparkle.data.hdf5data import HDF5Data


class TestBatlabData():
    def setup(self):
        self.datafile = BatlabData(sample.batlabfile())

    def teardown(self):
        self.datafile.close()

    def test_load_batlab(self):
        # check some things we know about the data
        all_tests = self.datafile.all_datasets()
        assert len(all_tests) == 13

    def test_keys(self):
        datakeys = self.datafile.keys()

        assert len(datakeys) == 13
        assert 'test_1' in datakeys
        assert 'test_13' in datakeys

    def test_get_info(self):

        info = self.datafile.get_info('test_1')
        assert info['testtype'] == "Tuning Curve"
        assert info['samplerate_ad'] == 40000

        info = self.datafile.get_info('test_3')
        assert info['testtype'] == "Input-Output Multiple Bat Call Test"
        assert info['samplerate_ad'] == 40000

        info = self.datafile.get_info('test_8')
        assert info['testtype'] == "General Auto Test"
        assert info['samplerate_ad'] == 40000

    def test_get_data(self):
        # test a few different shapes
        data = self.datafile.get_data('test_1')
        print 'data shape', data.shape
        assert data.shape == (10, 5, 4000)

        data = self.datafile.get_data('test_3')
        assert data.shape == (2, 5, 4000)

        data = self.datafile.get_data('test_13')
        assert data.shape == (4, 5, 4000)

    def test_get_trace_stim(self):
        stim = self.datafile.get_trace_stim('test_1')
        assert len(stim) == 10
        assert stim[0]['samplerate_da'] == 400000
        assert len(stim[0]['components']) == 0
        assert len(stim[1]['components']) == 2
        assert stim[1]['components'][1]['stim_type'] == "Pure Tone"
        assert stim[1]['components'][1]['frequency'] == 60000
        

        stim = self.datafile.get_trace_stim('test_3')
        assert len(stim) == 2
        assert stim[0]['samplerate_da'] == 333333
        assert len(stim[0]['components']) == 2
        assert stim[0]['components'][1]['stim_type'] == "Vocalization"
        assert stim[0]['components'][1]['filename'] == "94_14kHz_OLap3ms.call1"
