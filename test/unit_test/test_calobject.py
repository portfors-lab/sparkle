import numpy as np
import os
from audiolab.calibration.datatypes import CalibrationObject
import glob

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")

class TestCalObj():
    def setUp(self):
        print('setting up ob')
        self.freqs = [x for x in range(5,51,5)]
        self.intensities = [x for x in range(0,101,10)]
        self.samplerate = 400000
        self.duration = 200
        self.risefall = 5
        self.nreps = 3
        self.dbv = (100,0.1)

        self.caldata = CalibrationObject(self.freqs, self.intensities, self.samplerate, self.duration, 
                                         self.risefall, self.nreps,v=self.dbv[1])

    def tearDown(self):
        # delete generated file
        for filename in glob.glob(os.path.join(tempfolder,'savetemp.*')):
            os.remove(filename)

    def testcreate(self):

        assert self.caldata.stim['sr'] == self.samplerate
        assert self.caldata.stim['calV'] == self.dbv[1]
        assert self.caldata.stim['frequencies'] == self.freqs
        assert self.caldata.stim['intensities'] == self.intensities
        assert self.caldata.stim['duration'] == self.duration
        assert self.caldata.stim['risefalltime'] == self.risefall
        assert self.caldata.stim['repetitions'] == self.nreps

    def test_initdata(self):

        self.caldata.init_data('testdata', 2)
        assert self.caldata.data['testdata'].shape == (len(self.freqs), len(self.intensities))

        self.caldata.init_data('testdata', 3)
        assert self.caldata.data['testdata'].shape == (len(self.freqs), len(self.intensities), self.nreps)

        npts = (self.samplerate*(self.duration/1000))
        self.caldata.init_data('testdata', 4, dim4=npts)
        assert self.caldata.data['testdata'].shape == (len(self.freqs), len(self.intensities), self.nreps, npts)

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

    def test_save(self):
        npts = (self.samplerate*(self.duration/1000))
        self.caldata.init_data('testdata', 4, dim4=npts)
        d = np.ones(npts)
        
        self.caldata.put('testdata', (self.freqs[1], self.intensities[3], 1), d)

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

class TestCalObjFile():
    def setup(self):
        print("setting up file test")
        self.freqs = [x for x in range(5,51,5)]
        self.intensities = [x for x in range(0,101,10)]
        self.samplerate = 400000
        self.duration = 200
        self.risefall = 5
        self.nreps = 3
        self.dbv = (100,0.1)

        co =  CalibrationObject(self.freqs, self.intensities, self.samplerate, self.duration, 
                                         self.risefall, self.nreps,v=self.dbv[1])

        npts = (self.samplerate*(self.duration/1000))
        co.init_data('testdata', 4, dim4=npts)
        d = np.ones(npts)
        self.d = d
        
        co.put('testdata', (self.freqs[1], self.intensities[3], 1), d)
        
        self.filetypes = ['.json', '.mat', '.npy', '.pkl']
        for ext in self.filetypes:
            fname = os.path.join(tempfolder,'savetemp' + ext)
            co.save_to_file(fname)

        print(self.filetypes)

    def tearDown(self):
        # delete generated file
        for filename in glob.glob(os.path.join(tempfolder,'savetemp.*')):
            os.remove(filename)

    def test_loaded_calobj(self):
        # load it back in
        for ext in self.filetypes:
            fname = os.path.join(tempfolder,'savetemp' + ext)
            self.caldata = CalibrationObject.load_from_file(fname)
            yield self.verify_dictfields(), ext
            yield self.verify_get(), ext

    def verify_dictfields(self):

        assert self.caldata.stim['sr'] == self.samplerate
        assert self.caldata.stim['calV'] == self.dbv[1]
        assert self.caldata.stim['frequencies'] == self.freqs
        assert self.caldata.stim['intensities'] == self.intensities
        assert self.caldata.stim['duration'] == self.duration
        assert self.caldata.stim['risefalltime'] == self.risefall
        assert self.caldata.stim['repetitions'] == self.nreps

    def verify_get(self):
        
        dback = self.caldata.get('testdata', (self.freqs[1], self.intensities[3], 1))
        assert np.array_equal(dback,self.d)




