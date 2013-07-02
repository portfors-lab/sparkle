import os
import glob
from audiolab.io import fileio
import numpy as np
from nose.tools import with_setup

class TestSaveArray():
    def setUp(self):
        dims = (5,1000)
        self.sample_array = np.zeros(dims)

    def tearDown(self):
        # delete generated files
        for filename in glob.glob('savetemp.*'):
            os.remove(filename)
        

    def testtxt_auto(self):
        status = fileio.mightysave('savetemp.txt', self.sample_array)
        assert status == 0
        assert os.path.isfile('savetemp.txt')
    
    def testnpy_auto(self):
        status = fileio.mightysave('savetemp.npy', self.sample_array)
        assert status == 0
        assert os.path.isfile('savetemp.npy')

    def testmat_auto(self):
        status = fileio.mightysave('savetemp.mat', self.sample_array)
        assert status == 0
        assert os.path.isfile('savetemp.mat')

    def testpkl_auto(self):
        status = fileio.mightysave('savetemp.pkl', self.sample_array)
        assert status == 0
        assert os.path.isfile('savetemp.pkl')

    def testjson_auto(self):
        status = fileio.mightysave('savetemp.json', self.sample_array)
        assert status == 0
        assert os.path.isfile('savetemp.json')

    def testtxt(self):
        status = fileio.mightysave('savetemp', self.sample_array, filetype='txt')
        assert status == 0
        assert os.path.isfile('savetemp.txt')
    
    def testnpy(self):
        status = fileio.mightysave('savetemp', self.sample_array, filetype='npy')
        assert status == 0
        assert os.path.isfile('savetemp.npy')

    def testmat(self):
        status = fileio.mightysave('savetemp', self.sample_array, filetype='mat')
        assert status == 0
        assert os.path.isfile('savetemp.mat')

    def testpkl(self):
        status = fileio.mightysave('savetemp', self.sample_array, filetype='pkl')
        assert status == 0
        assert os.path.isfile('savetemp.pkl')

    def testjson(self):
        status = fileio.mightysave('savetemp', self.sample_array, filetype='json')
        assert status == 0
        assert os.path.isfile('savetemp.json')
