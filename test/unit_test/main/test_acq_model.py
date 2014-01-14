import sys, os, glob
import json

import h5py
from nose.tools import assert_in, assert_equal

from spikeylab.main.acqmodel import AcquisitionModel
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import *

import test.sample as sample

class TestAcquisitionModel():

    def setUp(self):
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

    def tearDown(self):
        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

    def test_tone_protocol(self):
        """Test a protocol with a single tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)

        #insert some stimuli
        gen_rate = 500000

        tone0 = PureTone()
        tone0.setDuration(0.02)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        stim0.setSamplerate(gen_rate)
        acqmodel.protocol_model.insertNewTest(stim0,0)

        t = acqmodel.run_protocol(0.25)
        t.join()

        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], gen_rate)
        assert_equal(test.shape,(1,1,winsz*acq_rate))

        hfile.close()

    def test_vocal_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)

        vocal0 = Vocalization()
        vocal0.setFile(sample.samplewav())
        stim0 = StimulusModel()
        stim0.insertComponent(vocal0)
        acqmodel.protocol_model.insertNewTest(stim0,0)

        t = acqmodel.run_protocol(0.25)
        t.join()

        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], vocal0.samplerate())
        assert_equal(test.shape,(1,1,winsz*acq_rate))

        hfile.close()

        

    def create_acqmodel(self, winsz, acq_rate):
        acqmodel = AcquisitionModel()

        acqmodel.set_params(aochan=u"PCI-6259/ao0", aichan=u"PCI-6259/ai0",
                            acqtime=winsz, aisr=acq_rate)

        acqmodel.set_save_params(self.tempfolder, 'testdata')
        fname = acqmodel.create_data_file()

        return acqmodel, fname