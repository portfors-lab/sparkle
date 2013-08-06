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
        for filename in glob.glob(u'savetemp.*'):
            os.remove(filename)
        

    def testtxt_auto(self):
        status = fileio.mightysave(u'savetemp.txt', self.sample_array)
        assert status == 0
        assert os.path.isfile(u'savetemp.txt')
    
    def testnpy_auto(self):
        status = fileio.mightysave(u'savetemp.npy', self.sample_array)
        assert status == 0
        assert os.path.isfile(u'savetemp.npy')

    def testmat_auto(self):
        status = fileio.mightysave(u'savetemp.mat', self.sample_array)
        assert status == 0
        assert os.path.isfile(u'savetemp.mat')

    def testpkl_auto(self):
        status = fileio.mightysave(u'savetemp.pkl', self.sample_array)
        assert status == 0
        assert os.path.isfile(u'savetemp.pkl')

    def testjson_auto(self):
        status = fileio.mightysave(u'savetemp.json', self.sample_array)
        assert status == 0
        assert os.path.isfile(u'savetemp.json')

    def testtxt(self):
        status = fileio.mightysave(u'savetemp', self.sample_array, filetype=u'txt')
        assert status == 0
        assert os.path.isfile(u'savetemp.txt')
    
    def testnpy(self):
        status = fileio.mightysave(u'savetemp', self.sample_array, filetype=u'npy')
        assert status == 0
        assert os.path.isfile(u'savetemp.npy')

    def testmat(self):
        status = fileio.mightysave(u'savetemp', self.sample_array, filetype=u'mat')
        assert status == 0
        assert os.path.isfile(u'savetemp.mat')

    def testpkl(self):
        status = fileio.mightysave(u'savetemp', self.sample_array, filetype=u'pkl')
        assert status == 0
        assert os.path.isfile(u'savetemp.pkl')

    def testjson(self):
        status = fileio.mightysave(u'savetemp', self.sample_array, filetype=u'json')
        assert status == 0
        assert os.path.isfile(u'savetemp.json')
