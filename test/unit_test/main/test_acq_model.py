import sys, os, glob
import json
import time
import threading, Queue

import h5py
from nose.tools import assert_in, assert_equal

from spikeylab.main.acqmodel import AcquisitionModel
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization
from spikeylab.stim.tceditor import TCFactory
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import Qt

import test.sample as sample

class TestAcquisitionModel():

    def setUp(self):
        self.app = QApplication(sys.argv)
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        self.done = True

    def tearDown(self):
        # bit of a hack to wait for chart acquisition to finish
        while not self.done:
            time.sleep(1)
        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)
        self.app.exit(0)

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

    def test_tone_protocol_uncalibrated(self):
        """Test a protocol with a single tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)
        acqmodel.set_calibration(None)
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
        """Run protocol with single vocal wav stimulus"""
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

    def test_auto_parameter_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)

        component = PureTone()
        stim_model = StimulusModel()
        stim_model.insertComponent(component, (0,0))
        auto_model = stim_model.autoParams()
        auto_model.insertRows(0, 1)
        
        selection_model = auto_model.data(auto_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim_model.index(0,0))

        values = ['frequency', 0, 100, 10]
        for i, value in enumerate(values):
            auto_model.setData(auto_model.index(0,i), value, Qt.EditRole)

        acqmodel.protocol_model.insertNewTest(stim_model,0)

        t = acqmodel.run_protocol(0.25)
        t.join()

        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stims = json.loads(test.attrs['stim'])

        freqs = []
        for stim in stims:
            freqs.append(stim['components'][0]['frequency'])

        assert freqs == sorted(freqs)
        assert_equal(stims[0]['samplerate_da'], stim_model.samplerate())
        assert_equal(test.shape,(11,1,winsz*acq_rate))

        hfile.close()

    def test_auto_parameter_protocol_randomize(self):
        from spikeylab.stim.auto_parameters_editor import random_order
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)

        component = PureTone()
        stim_model = StimulusModel()
        stim_model.insertComponent(component, (0,0))
        stim_model.reorder = random_order
        auto_model = stim_model.autoParams()
        auto_model.insertRows(0, 1)
        
        selection_model = auto_model.data(auto_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim_model.index(0,0))

        values = ['frequency', 0, 100, 10]
        for i, value in enumerate(values):
            auto_model.setData(auto_model.index(0,i), value, Qt.EditRole)

        acqmodel.protocol_model.insertNewTest(stim_model,0)

        t = acqmodel.run_protocol(0.25)
        t.join()

        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stims = json.loads(test.attrs['stim'])
        #get a list of the freqency order
        freqs = []
        for stim in stims:
            freqs.append(stim['components'][0]['frequency'])

        assert freqs != sorted(freqs)
        assert_equal(stims[0]['samplerate_da'], stim_model.samplerate())
        assert_equal(test.shape,(11,1,winsz*acq_rate))

        hfile.close()


    def test_tone_explore(self):
        """Run search operation with tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)        

        acqmodel.set_params(nreps=2)
        stim_names = acqmodel.explore_stim_names()
        acqmodel.set_stim_by_index(stim_names.index('Pure Tone'))
        t = acqmodel.run_explore(0.25)

        time.sleep(1)

        acqmodel.halt()

        t.join()
        acqmodel.close_data()

        # now check saved data
        # hfile = h5py.File(os.path.join(self.tempfolder, fname))
        # test = hfile['explore_0']
        # stim = json.loads(test.attrs['stim'])

        # assert_in('components', stim[0])
        # assert_equal(stim[0]['samplerate_da'], acqmodel.stimulus.samplerate())
        # assert_equal(test.shape[1], winsz*acq_rate)

        # hfile.close()

    def test_vocal_explore(self):
        """Run search operation with vocal wav stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)        

        acqmodel.set_params(nreps=2)
        stim_names = acqmodel.explore_stim_names()

        acqmodel.explore_stimuli[stim_names.index('Vocalization')].setFile(sample.samplewav())
        acqmodel.set_stim_by_index(stim_names.index('Vocalization'))
        
        t = acqmodel.run_explore(0.25)

        time.sleep(1)

        acqmodel.halt()

        t.join()
        acqmodel.close_data()

        # now check saved data
        # hfile = h5py.File(os.path.join(self.tempfolder, fname))
        # test = hfile['explore_0']
        # stim = json.loads(test.attrs['stim'])

        # assert_in('components', stim[0])
        # assert_equal(stim[0]['samplerate_da'], acqmodel.stimulus.samplerate())
        # assert_equal(test.shape[1], winsz*acq_rate)

        # hfile.close()

    def test_tuning_curve(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)

        tc = StimulusModel()
        TCFactory().init_stim(tc)
        nreps = tc.repCount()
        ntraces = tc.traceCount()

        acqmodel.protocol_model.insertNewTest(tc,0)

        t = acqmodel.run_protocol(0.25)
        t.join()

        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], tc.samplerate())
        assert_equal(test.shape,(ntraces,nreps,winsz*acq_rate))

        hfile.close()

    def test_chart_no_stim(self):
        winsz = 1.0 # this is actually ignored by acqmodel in this case
        acq_rate = 100000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)
        acqmodel.set_params(savechart=True)
        acqmodel.start_chart()
        self.done = False
        self.timer = threading.Timer(1.0, self.stopchart, args=(acqmodel, fname))
        self.timer.start()

    def stopchart(self, acqmodel, fname):
        acqmodel.stop_chart()
        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['chart_0']
        stim = json.loads(test.attrs['stim'])
        assert stim == []
        assert test.size > 1
        assert len(test.shape) == 1

        hfile.close()
        self.done = True

    def test_chart_tone_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)
        acqmodel.set_params(savechart=True)

        #insert some stimuli
        gen_rate = 500000

        tone0 = PureTone()
        tone0.setDuration(0.2)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        stim0.setSamplerate(gen_rate)
        acqmodel.protocol_model.insertNewTest(stim0,0)

        acqmodel.start_chart()
        t = acqmodel.run_chart_protocol(0.25)
        t.join()

        acqmodel.stop_chart()
        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['chart_0']
        stim = json.loads(test.attrs['stim'])

        print 'stim', stim
        # assert_in('components', stim[0])
        # assert_equal(stim[0]['samplerate_da'], gen_rate)
        assert_equal(test.shape,(winsz*acq_rate,))
        assert len(test.shape) == 1
        
        hfile.close()

    def test_calibration_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 500000
        acqmodel, fname = self.create_acqmodel(winsz, acq_rate)

        tc = acqmodel.calibration_stimulus
        ntraces = tc.traceCount()
        nreps = tc.repCount()
        # tc.autoParameters()
        # use tuning curve defaults?
        t, calname = acqmodel.run_calibration(0.25, False)
        t.join()
        acqmodel.process_calibration()
        acqmodel.close_data()

        # now check saved data
        hfile = h5py.File(calname, 'r')
        peaks = hfile['fft_peaks']
        stim = json.loads(hfile.attrs['stim'])
        cal_vector = hfile['calibration_intensities']

        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], tc.samplerate())
        assert_equal(peaks.shape,(ntraces,nreps))
        assert cal_vector.shape == (21,) #beware, will fail if defaults change

        hfile.close()

    def create_acqmodel(self, winsz, acq_rate):
        acqmodel = AcquisitionModel()

        acqmodel.set_params(aochan=u"PCI-6259/ao0", aichan=u"PCI-6259/ai0",
                            acqtime=winsz, aisr=acq_rate)
        acqmodel.set_calibration(sample.calibration_filename())

        acqmodel.set_save_params(self.tempfolder, 'testdata')
        fname = acqmodel.create_data_file()

        return acqmodel, fname
