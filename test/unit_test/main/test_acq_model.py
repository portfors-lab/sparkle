import sys, os
import json

import h5py
from nose.tools import assert_in, assert_equal

from spikeylab.main.acqmodel import AcquisitionModel
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import *

class TestAcquisitionModel():

    def setUp(self):
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

    def tearDown(self):
        os.remove(os.path.join(self.tempfolder, 'testdata0.hdf5'))

    def test_tone_protocol(self):
        acqmodel = AcquisitionModel()
        winsz = 0.2 #seconds
        acq_rate = 50000
        gen_rate = 500000
        acqmodel.set_params(aochan=u"PCI-6259/ao0", aichan=u"PCI-6259/ai0",
                            acqtime=winsz, aisr=acq_rate, aosr=gen_rate)

        acqmodel.set_save_params(self.tempfolder, 'testdata')
        acqmodel.create_data_file()

        #insert some stimuli
        tone0 = PureTone()
        tone0.setDuration(0.02)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        acqmodel.protocol_model.insertNewTest(stim0,0)

        t = acqmodel.run_protocol(0.25)
        t.join()

        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, 'testdata0.hdf5'))
        test = hfile['segment_0']['test_0']
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(test.shape,(1,1,winsz*acq_rate))

        hfile.close()

