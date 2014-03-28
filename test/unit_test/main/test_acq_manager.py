import sys, os, glob
import json
import time
import threading, Queue

import h5py
from nose.tools import assert_in, assert_equal

from spikeylab.main.acquisition_manager import AcquisitionManager
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization
from spikeylab.stim.reorder import random_order
from spikeylab.stim.factory import TCFactory
from PyQt4.QtCore import Qt

import test.sample as sample

class TestAcquisitionModel():

    def setUp(self):
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

    def test_tone_protocol(self):
        """Test a protocol with a single tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        #insert some stimuli
        gen_rate = 500000

        tone0 = PureTone()
        tone0.setDuration(0.02)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        stim0.setSamplerate(gen_rate)
        manager.protocol_model().insertNewTest(stim0,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

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
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        manager.set_calibration(None)
        #insert some stimuli
        gen_rate = 500000

        tone0 = PureTone()
        tone0.setDuration(0.02)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        stim0.setSamplerate(gen_rate)
        manager.protocol_model().insertNewTest(stim0,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], gen_rate)
        assert_equal(test.shape,(1,1,winsz*acq_rate))
        assert stim[0]['overloaded_attenuation'] == 0

        hfile.close()

    def test_tone_protocol_over_voltage(self):
        """Test a protocol with a single tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        #insert some stimuli
        gen_rate = 500000

        tone0 = PureTone()
        tone0.setDuration(0.02)
        tone0.setIntensity(manager.protocoler.caldb)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        stim0.setSamplerate(gen_rate)
        manager.protocol_model().insertNewTest(stim0,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], gen_rate)
        assert_equal(test.shape,(1,1,winsz*acq_rate))
        assert stim[0]['overloaded_attenuation'] > 0
        hfile.close()

    def test_vocal_protocol(self):
        """Run protocol with single vocal wav stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        vocal0 = Vocalization()
        vocal0.setFile(sample.samplewav())
        stim0 = StimulusModel()
        stim0.insertComponent(vocal0)
        manager.protocol_model().insertNewTest(stim0,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

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
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        nreps = 3
        component = PureTone()
        stim_model = StimulusModel()
        stim_model.insertComponent(component, (0,0))
        stim_model.setRepCount(nreps)
        auto_model = stim_model.autoParams()
        auto_model.insertRows(0, 1)
        
        selection_model = auto_model.data(auto_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim_model.index(0,0))

        values = ['frequency', 0, 100, 10]
        for i, value in enumerate(values):
            auto_model.setData(auto_model.index(0,i), value, Qt.EditRole)

        manager.protocol_model().insertNewTest(stim_model,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()
        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stims = json.loads(test.attrs['stim'])
        freqs = []
        for stim in stims:
            freqs.append(stim['components'][0]['frequency'])

        assert freqs == sorted(freqs)
        assert_equal(stims[0]['samplerate_da'], stim_model.samplerate())
        assert_equal(test.shape,(11,nreps,winsz*acq_rate))

        hfile.close()

    def test_auto_parameter_protocol_randomize(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

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

        manager.protocol_model().insertNewTest(stim_model,0)
        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()
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
        manager, fname = self.create_acqmodel(winsz, acq_rate)        

        manager.set_params(nreps=2)
        stim_names = manager.explore_stim_names()
        manager.set_stim_by_index(stim_names.index('Pure Tone'))
        t = manager.run_explore(0.25)

        time.sleep(1)

        manager.halt()

        t.join()
        manager.close_data()

        # should check that it did not save data!


    def test_vocal_explore(self):
        """Run search operation with vocal wav stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)        

        manager.set_params(nreps=2)
        stim_names = manager.explore_stim_names()

        # cheat - private access
        manager.explorer._explore_stimuli[stim_names.index('Vocalization')].setFile(sample.samplewav())
        manager.set_stim_by_index(stim_names.index('Vocalization'))
        
        t = manager.run_explore(0.25)

        time.sleep(1)

        manager.halt()

        t.join()
        manager.close_data()

    def test_tone_vocal_explore_save(self):
        """Run search operation with tone and vocal stimulus, and save results"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)        

        manager.set_params(nreps=2, save=True)
        stim_names = manager.explore_stim_names()
        manager.set_stim_by_index(stim_names.index('Pure Tone'))
        t = manager.run_explore(0.25)

        time.sleep(1)

        # cheat to set vocal file :(
        manager.explorer._explore_stimuli[stim_names.index('Vocalization')].setFile(sample.samplewav())
        manager.set_stim_by_index(stim_names.index('Vocalization'))

        time.sleep(1)

        manager.halt()

        t.join()
        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        print hfile.keys()
        test = hfile['explore_0']
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(stim[-1]['samplerate_da'], manager.explore_genrate())
        assert_equal(test.shape[1], winsz*acq_rate)

        hfile.close()

    def test_tuning_curve(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        tc = StimulusModel()
        TCFactory().init_stim(tc)
        nreps = tc.repCount()
        ntraces = tc.traceCount()

        manager.protocol_model().insertNewTest(tc,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_0']['test_0']
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], tc.samplerate())
        assert_equal(test.shape,(ntraces,nreps,winsz*acq_rate))

        hfile.close()

    def test_chart_no_stim(self):
        winsz = 1.0 # this is actually ignored by manager in this case
        acq_rate = 100000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        manager.set_params(savechart=True)
        manager.start_chart()
        self.done = False
        self.timer = threading.Timer(1.0, self.stopchart, args=(manager, fname))
        self.timer.start()

    def stopchart(self, manager, fname):
        manager.stop_chart()
        manager.close_data()

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
        winsz = 0.1 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        manager.set_params(savechart=True)

        #insert some stimuli
        gen_rate = 500000

        tone0 = PureTone()
        tone0.setDuration(winsz)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        stim0.setSamplerate(gen_rate)
        manager.protocol_model().insertNewTest(stim0,0)

        manager.start_chart()
        t = manager.run_chart_protocol(0.15)
        t.join()

        manager.stop_chart()
        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['chart_0']
        stim = json.loads(test.attrs['stim'])

        print 'stim', stim
        # assert_in('components', stim[0])
        # assert_equal(stim[0]['samplerate_da'], gen_rate)
        assert len(test.shape) == 1
        assert test.shape[0] >= winsz*acq_rate
        
        hfile.close()

    def test_calibration_protocol(self):
        winsz = 0.1 #seconds
        acq_rate = 500000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        tc = manager.calibration_stimulus('tone')
        ntraces = tc.traceCount()
        nreps = tc.repCount()
        # tc.autoParameters()
        # use tuning curve defaults?
        manager.set_calibration_duration(winsz)
        t = manager.run_calibration(0.1, False)
        t.join()
        calname = manager.process_calibration()
        manager.close_data()

        # now check saved data
        hfile = h5py.File(calname, 'r')
        peaks = hfile['fft_peaks']
        # signals = hfile['signal']
        stim = json.loads(hfile.attrs['stim'])
        cal_vector = hfile['calibration_intensities']

        assert_in('components', stim[0])
        assert_equal(stim[0]['samplerate_da'], tc.samplerate())
        assert_equal(peaks.shape,(ntraces,nreps))
        # npts =  winsz*acq_rate
        # assert_equal(signals.shape,(nreps, npts))
        
        assert cal_vector.shape == (21,) #beware, will fail if defaults change
        # assert cal_vector.shape == ((npts/2+1),)

        hfile.close()

    def create_acqmodel(self, winsz, acq_rate):
        manager = AcquisitionManager()

        manager.set_params(aochan=u"PCI-6259/ao0", aichan=u"PCI-6259/ai0",
                            acqtime=winsz, aisr=acq_rate, caldb=100,
                            calv=1.0)
        manager.set_calibration(sample.calibration_filename())

        manager.set_save_params(self.tempfolder, 'testdata')
        fname = manager.create_data_file()

        return manager, fname
