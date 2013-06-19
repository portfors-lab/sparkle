import fileio
import numpy as np
from nose.tools import with_setup

class TestSave():
    def setUp(self):
        dims = (5,1000)
        self.sample_array = np.zeros(dims)

    def teardown(self):
        pass

    #@with_setup(setup,teardown)
    def testtxt(self):
        status = cougario.mightysave('save.txt', self.sample_array)
        assert status == 0
    
    def testnpy(self):
        status = cougario.mightysave('save.npy', self.sample_array)
        assert status == 0

    def testmat(self):
        status = cougario.mightysave('save.mat', self.sample_array)
        assert status == 0

    def testpkl(self):
        status = cougario.mightysave('save.pkl', self.sample_array)
        assert status == 0

    def testjson(self):
        status = cougario.mightysave('save.json', self.sample_array)
        assert status == 0

