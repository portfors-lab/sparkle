import os
import glob
from spikeylab.io import fileio
import numpy as np
from nose.tools import with_setup

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp")
fname = os.path.join(tempfolder,'savetemp')

class TestSaveArray():
    def setUp(self):
        dims = (5,1000)
        self.sample_array = np.zeros(dims)

    def tearDown(self):
        # delete generated files
        for filename in glob.glob(fname + '.*'):
            os.remove(filename)
        

    def testtxt_auto(self):
        status = fileio.mightysave(fname+'.txt', self.sample_array)
        assert status == 0
        assert os.path.isfile(fname+'.txt')
    
    def testnpy_auto(self):
        status = fileio.mightysave(fname+'.npy', self.sample_array)
        assert status == 0
        assert os.path.isfile(fname+'.npy')

    def testmat_auto(self):
        status = fileio.mightysave(fname+u'.mat', self.sample_array)
        assert status == 0
        assert os.path.isfile(fname + u'.mat')

    def testpkl_auto(self):
        status = fileio.mightysave(fname + u'.pkl', self.sample_array)
        assert status == 0
        assert os.path.isfile(fname + u'.pkl')

    def testjson_auto(self):
        status = fileio.mightysave(fname+'.json', self.sample_array)
        assert status == 0
        assert os.path.isfile(fname+u'.json')

    def testtxt(self):
        status = fileio.mightysave(fname, self.sample_array, filetype=u'txt')
        assert status == 0
        assert os.path.isfile(fname+u'.txt')
    
    def testnpy(self):
        status = fileio.mightysave(fname, self.sample_array, filetype=u'npy')
        assert status == 0
        assert os.path.isfile(fname+u'.npy')

    def testmat(self):
        status = fileio.mightysave(fname, self.sample_array, filetype=u'mat')
        assert status == 0
        assert os.path.isfile(fname+u'.mat')

    def testpkl(self):
        status = fileio.mightysave(fname, self.sample_array, filetype=u'pkl')
        assert status == 0
        assert os.path.isfile(fname + u'.pkl')

    def testjson(self):
        status = fileio.mightysave(fname, self.sample_array, filetype=u'json')
        assert status == 0
        assert os.path.isfile(fname +u'.json')
