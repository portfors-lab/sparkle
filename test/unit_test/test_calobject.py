import numpy as np
import os
from audiolab.calibration.datatypes import CalibrationObject
import glob
from nose.tools import nottest

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")

class TestCalObj():
    """
    Test creating, putting and getting to calibration data structure
    """
    def setUp(self):
        print('setting up ob')
        self.freqs = [x for x in range(5,51,5)]
        self.intensities = [x for x in range(0,101,10)]
        self.samplerate = 100000
        self.duration = 200
        self.risefall = 5
        self.nreps = 3
        self.dbv = (100,0.1)

        fname = os.path.join(tempfolder,'savetemp.hdf5')
        self.caldata = CalibrationObject(fname, self.freqs, self.intensities, self.samplerate, 
                                         self.duration, self.risefall, self.nreps,v=self.dbv[1])

    def tearDown(self):
        # delete generated file
        self.caldata.hdf5.close()
        for filename in glob.glob(os.path.join(tempfolder,'savetemp.*')):
            os.remove(filename)

    def testcreate(self):
        print("inside test create")
        assert self.caldata.attrs['sr'] == self.samplerate
        assert self.caldata.attrs['calv'] == self.dbv[1]
        assert np.array_equal(self.caldata.attrs['frequencies'], self.freqs)
        assert np.array_equal(self.caldata.attrs['intensities'], self.intensities)
        assert self.caldata.attrs['duration'] == self.duration
        assert self.caldata.attrs['risefalltime'] == self.risefall
        assert self.caldata.attrs['repetitions'] == self.nreps

    def test_initdata(self):

        self.caldata.init_data('testdata2', 2)
        assert self.caldata.data['testdata2'].shape == (len(self.freqs), 
                                                       len(self.intensities))

        self.caldata.init_data('testdata3', 3)
        assert self.caldata.data['testdata3'].shape == (len(self.freqs), 
                                                       len(self.intensities), self.nreps)

        npts = (self.samplerate*(self.duration/1000))
        self.caldata.init_data('testdata4', 4, dim4=npts)
        assert self.caldata.data['testdata4'].shape == (len(self.freqs), 
                                                       len(self.intensities), self.nreps, 
                                                       npts)

    def test_put(self):
        npts = (self.samplerate*(self.duration/1000))
        self.caldata.init_data('testdata', 4, dim4=npts)
        d = np.ones(npts)
        
        self.caldata.put('testdata', (self.freqs[1], self.intensities[3], 1), d)
        #print(self.caldata.data['testdata'][1][3][1].shape, d.shape)
        assert np.array_equal(self.caldata.data['testdata'][1,3,1],d)
        assert not np.array_equal(self.caldata.data['testdata'][1,3,0],d)

    def test_get(self):

        npts = (self.samplerate*(self.duration/1000))
        self.caldata.init_data('testdata', 4, dim4=npts)
        d = np.ones(npts)
        
        self.caldata.put('testdata', (self.freqs[1], self.intensities[3], 1), d)
        dback = self.caldata.get('testdata', (self.freqs[1], self.intensities[3], 1))
        assert np.array_equal(dback,d)

    def xtest_save(self):
        npts = (self.samplerate*(self.duration/1000))
        self.caldata.init_data('testdata', 4, dim4=npts)
        d = np.ones(npts)
        
        self.caldata.put('testdata', (self.freqs[1], self.intensities[3], 1), d)

        """
        fname = os.path.join(tempfolder,'savetemp.json')
        self.caldata.save_to_file(fname)
        assert os.path.isfile(fname)

        fname = os.path.join(tempfolder,'savetemp.mat')
        self.caldata.save_to_file(fname)
        assert os.path.isfile(fname)

        fname = os.path.join(tempfolder,'savetemp.npy')
        self.caldata.save_to_file(fname)
        assert os.path.isfile(fname)

        fname = os.path.join(tempfolder,'savetemp.pkl')
        self.caldata.save_to_file(fname)
        assert os.path.isfile(fname)
        """

        fname = os.path.join(tempfolder,'savetemp.hdf5')
        self.caldata.save_to_file(fname)
        assert os.path.isfile(fname)
