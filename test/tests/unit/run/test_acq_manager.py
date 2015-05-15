import glob
import json
import logging
import os
import Queue
import StringIO
import sys
import threading
import time
import unittest

import h5py
import numpy as np
from nose.tools import assert_equal, assert_in, nottest

import test.sample as sample
from test.tests.unit.data.test_hdf5_data import assert_attrs_equal
from sparkle.data.open import open_acqdata
from sparkle.gui.stim.factory import TCFactory
from sparkle.run.acquisition_manager import AcquisitionManager
from sparkle.stim.auto_parameter_model import AutoParameterModel
from sparkle.stim.reorder import random_order
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import PureTone, Silence, Vocalization
from sparkle.tools.systools import rand_id


class TestAcquisitionManager():

    def setUp(self):
        StimulusModel.setMaxVoltage(1.5, 10.0)
        StimulusModel.setMinVoltage(0.005)
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        self.done = True

        log = logging.getLogger('main')
        log.setLevel(logging.DEBUG)
        self.stream = StringIO.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        log.addHandler(self.handler)


    def tearDown(self):
        # bit of a hack to wait for chart acquisition to finish
        while not self.done:
            time.sleep(1)
        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

        assert "Error:" not in self.stream.getvalue()
        log = logging.getLogger('main')
        log.removeHandler(self.handler)
        self.handler.close()


    def tone_protocol(self, manager, intensity=70):
        #insert some stimuli

        tone = PureTone()
        tone.setDuration(0.02)
        tone.setIntensity(intensity)
        stim = StimulusModel()
        stim.insertComponent(tone)
        manager.protocol_model().insert(stim,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()
        
        return stim

    def test_tone_protocol(self):
        """Test a protocol with a single tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        self.fake_calibration(manager)

        # create and run tone protocol
        stim = self.tone_protocol(manager)

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, stim, winsz, acq_rate)

        assert 'calibration_' in hfile['segment_1'].attrs['calibration_used']

        hfile.close()

    def test_tone_protocol_data_backup(self):
        """functional test for data backup"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        # create and run tone protocol
        self.tone_protocol(manager)

        # close without backup clean up
        manager.datafile.hdf5.close()

        # this will cause data to load from backups
        data_filepath = os.path.join(self.tempfolder, fname)
        backup_hfile = open_acqdata(data_filepath, filemode='r')
        base_fname, ext = os.path.splitext(data_filepath)
        original_hfile = open_acqdata(base_fname+'_compromised0'+ext, filemode='r')

        # check all their contents are equal
        assert backup_hfile.dataset_names() == original_hfile.dataset_names()
        assert_attrs_equal(original_hfile.hdf5, backup_hfile.hdf5)

        original_hfile.close()
        backup_hfile.close()

    def test_tone_protocol_no_attenuator(self):
        """Test a protocol with a single tone stimulus and no
        attenution for small amplitude"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        self.fake_calibration(manager)

        manager.attenuator_connection(False)
        # create and run tone protocol
        stim = self.tone_protocol(manager, intensity=10)

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, stim, winsz, acq_rate)

        assert 'calibration_' in hfile['segment_1'].attrs['calibration_used']

        assert stim.signal()[0].max() < 0.005

        hfile.close()

    def test_tone_protocol_with_attenuator(self):
        """Test a protocol with a single tone stimulus and no
        attenution for small amplitude"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        self.fake_calibration(manager)

        connected = manager.attenuator_connection(True)
        # create and run tone protocol
        stim = self.tone_protocol(manager, intensity=10)

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, stim, winsz, acq_rate)

        assert 'calibration_' in hfile['segment_1'].attrs['calibration_used']

        # print stim.signal()[0].max()
        if connected:
            assert np.around(stim.signal()[0].max(),5) == 0.005
        else:
            assert stim.signal()[0].max() < 0.005
            
        hfile.close()

    def test_tone_protocol_uncalibrated(self):
        """Test a protocol with a single tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        manager.set_calibration(None)
        #insert some stimuli

        tone0 = PureTone()
        tone0.setDuration(0.02)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        manager.protocol_model().insert(stim0,0)
        gen_rate = stim0.samplerate()

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        stim = json.loads(test.attrs['stim'])

        check_result(test, stim0, winsz, acq_rate)

        assert hfile['segment_1'].attrs['calibration_used'] == '' 

        hfile.close()

    def test_tone_protocol_over_voltage(self):
        """Test a protocol with a single tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        self.fake_calibration(manager)
        #insert some stimuli

        tone0 = PureTone()
        tone0.setDuration(0.02)
        tone0.setIntensity(120)
        tone0.setFrequency(90000)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        manager.protocol_model().insert(stim0,0)
        gen_rate = stim0.samplerate()

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']
        stim = json.loads(test.attrs['stim'])

        # stim 0 is control window
        assert_in('components', stim[1])
        assert_equal(stim[1]['samplerate_da'], gen_rate)
        assert_equal(test.shape,(2,1,1,winsz*acq_rate))
        assert stim[1]['overloaded_attenuation'] > 0
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
        manager.protocol_model().insert(stim0,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, stim0, winsz, acq_rate)

        hfile.close()

    def test_auto_parameter_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        nreps = 3
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        stim_model = create_tone_stim(nreps)

        manager.protocol_model().insert(stim_model,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()
        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, stim_model, winsz, acq_rate)

        hfile.close()

    def test_auto_parameter_protocol_randomize(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        nreps = 1
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        stim_model = create_tone_stim(nreps)
        stim_model.setReorderFunc(random_order, name='random')

        manager.protocol_model().insert(stim_model,0)
        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()
        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, stim_model, winsz, acq_rate)

        hfile.close()

    def test_auto_vocal_parameter_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        nreps = 3
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        stim_model = create_vocal_stim(nreps)

        manager.protocol_model().insert(stim_model,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()
        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, stim_model, winsz, acq_rate)

        hfile.close()

    def test_multichannel_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        nreps = 3
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        manager.set(aichan=[u"PCI-6259/ai0", u"PCI-6259/ai1"])

        stim_model = create_vocal_stim(nreps)

        manager.protocol_model().insert(stim_model,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()
        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, stim_model, winsz, acq_rate, 2)

        hfile.close()

    def test_abort_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        manager.set_calibration(None)
        #insert some stimuli
        tone0 = PureTone()
        tone0.setDuration(0.02)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        stim0.setRepCount(500) # set really high so we don't miss
        manager.protocol_model().insert(stim0,0)
        gen_rate = stim0.samplerate()

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        manager.halt()
        t.join()
        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        group = hfile['segment_1']

        assert group.attrs.get('aborted') is not None
        abort_msg = group.attrs['aborted']
        assert abort_msg.startswith("test 1, trace 0, rep")

        hfile.close()

    # @unittest.skip("Grrrrrr")
    def test_protocol_timing(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        nreps = 4
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        stim_model = create_tone_stim(nreps)

        manager.protocol_model().insert(stim_model,0)

        interval = 250
        manager.setup_protocol(interval)
        t = manager.run_protocol()
        t.join()

        manager.close_data()
        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']
        stims = json.loads(test.attrs['stim'])

        # aggregate all time intervals
        intervals = []
        for stim in stims:
            intervals.extend(stim['time_stamps'])
        intervals = np.diff(intervals)
        intervals = abs(intervals*1000 - interval)
        print 'all intervals', intervals.shape, intervals

        # ms tolerance, not as good as I would like
        assert all(map(lambda x: x < 10, intervals))

        hfile.close()

    # @unittest.skip("Grrrrrr")
    def test_protocol_timing_vocal_batlab(self):
        winsz = 0.280 #seconds
        acq_rate = 100000
        nreps = 4
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        with open(sample.batlabvocal(), 'r') as jf:
            state = json.load(jf)

        stim_model = StimulusModel.loadFromTemplate(state)
        manager.protocol_model().insert(stim_model,0)

        interval = 333
        manager.setup_protocol(interval)
        t = manager.run_protocol()
        t.join()

        manager.close_data()
        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']
        stims = json.loads(test.attrs['stim'])

        # aggregate all time intervals
        intervals = []
        for stim in stims:
            intervals.extend(stim['time_stamps'])
        intervals = np.diff(intervals)
        intervals = abs(intervals*1000 - interval)
        print 'all intervals', intervals.shape, intervals

        # ms tolerance, not as good as I would like
        assert all(map(lambda x: x < 10, intervals))

        hfile.close()

    def test_tone_explore(self):
        """Run search operation with tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        self.data = []
        # set a callback to gather and assert for data
        manager.set_queue_callback('response_collected', self.collect_response)
        manager.start_listening()        

        manager.set(nreps=2)
        stim = manager.explore_stimulus()
        stim.insertComponent(PureTone())
        t = manager.run_explore(0.25)

        time.sleep(1)

        manager.halt()

        t.join()
        manager.close_data()

        assert len(self.data) > 1
        times, dset = self.data[0]
        assert times.shape == (int(acq_rate*winsz),)
        assert dset.shape == (1, int(acq_rate*winsz))
        # should check that it did not save data!


    def test_vocal_explore(self):
        """Run search operation with vocal wav stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        self.data = []
        # set a callback to gather and assert for data
        manager.set_queue_callback('response_collected', self.collect_response)
        manager.start_listening()        

        manager.set(nreps=2)

        stim = manager.explore_stimulus()
        vocal = Vocalization()
        vocal.setFile(sample.samplewav())
        stim.insertComponent(vocal)
        
        t = manager.run_explore(0.25)

        time.sleep(1)

        manager.halt()

        t.join()
        manager.close_data()

        assert len(self.data) > 1
        times, dset = self.data[0]
        assert times.shape == (int(acq_rate*winsz),)
        assert dset.shape == (1, int(acq_rate*winsz))

    def test_multichannel_explore(self):
        """Run search operation with tone stimulus"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)        
        manager.set(aichan=[u"PCI-6259/ai0", u"PCI-6259/ai1"])

        self.data = []
        # set a callback to gather and assert for data
        manager.set_queue_callback('response_collected', self.collect_response)
        manager.start_listening()

        manager.set(nreps=2)
        stim = manager.explore_stimulus()
        stim.insertComponent(PureTone())
        t = manager.run_explore(0.25)

        time.sleep(1)

        manager.halt()

        t.join()
        manager.close_data()

        assert len(self.data) > 1
        times, dset = self.data[0]
        assert times.shape == (int(acq_rate*winsz),)
        assert dset.shape == (2, int(acq_rate*winsz))

    def collect_response(self, times, response, test_num, trace_num, rep_num, extra_info={}):
        self.data.append((times, response))

    def test_tone_vocal_explore_save(self):
        """Run search operation with tone and vocal stimulus, and save results"""
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)        

        manager.set(nreps=2, save=True)
        stim = manager.explore_stimulus()
        stim.insertComponent(PureTone())

        manager.reset_explore_stim()
        t = manager.run_explore(0.25)

        time.sleep(1)

        stim.removeComponent(0,0)

        vocal = Vocalization()
        vocal.setFile(sample.samplewav())
        stim.insertComponent(vocal)
        manager.reset_explore_stim()

        time.sleep(2)

        manager.halt()

        t.join()
        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        # print hfile.keys()
        test = hfile['explore_1']

        # check_result(test, manager.explorer.stimulus, winsz, acq_rate)
        stim = json.loads(test.attrs['stim'])

        assert_in('components', stim[0])
        assert_equal(stim[-1]['samplerate_da'], manager.explore_genrate())
        assert_equal(test.shape[1], winsz*acq_rate)

        hfile.close()

    def test_tuning_curve(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)

        tc = TCFactory().create()
        ntraces = tc.traceCount()

        manager.protocol_model().insert(tc,0)

        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['segment_1']['test_1']

        check_result(test, tc, winsz, acq_rate)

        # stim = json.loads(test.attrs['stim'])

        # assert_in('components', stim[0])
        # assert_equal(stim[0]['samplerate_da'], tc.samplerate())
        # assert_equal(test.shape,(ntraces,nreps,winsz*acq_rate))

        hfile.close()

    @nottest
    def test_chart_no_stim(self):
        winsz = 1.0 # this is actually ignored by manager in this case
        acq_rate = 100000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        manager.set(savechart=True)
        manager.start_chart()
        self.done = False
        self.timer = threading.Timer(1.0, self.stopchart, args=(manager, fname))
        self.timer.start()

    def stopchart(self, manager, fname):
        manager.stop_chart()
        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['chart_1']
        stim = json.loads(test.attrs['stim'])
        assert stim == []
        assert test.size > 1
        assert len(test.shape) == 1

        hfile.close()
        self.done = True

    @nottest
    def test_chart_tone_protocol(self):
        winsz = 0.1 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        manager.set(savechart=True)

        #insert some stimuli

        tone0 = PureTone()
        tone0.setDuration(winsz)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        manager.protocol_model().insert(stim0,0)
        gen_rate = stim0.samplerate()

        manager.start_chart()
        t = manager.run_chart_protocol(0.15)
        t.join()

        manager.stop_chart()
        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        test = hfile['chart_1']
        stim = json.loads(test.attrs['stim'])

        # print 'stim', stim
        # assert_in('components', stim[0])
        # assert_equal(stim[0]['samplerate_da'], gen_rate)
        assert len(test.shape) == 1
        assert test.shape[0] >= winsz*acq_rate
        
        hfile.close()

    def test_tone_calibration_protocol(self):
        winsz = 0.1 #seconds
        manager, fname = self.create_acqmodel(winsz)
        acq_rate = manager.calibration_genrate()

        manager.set_calibration_by_index(2)
        manager.set_mphone_calibration(0.004, 94)
        tc = manager.calibration_stimulus('tone')
        ntraces = tc.traceCount()
        nreps = tc.repCount()
        # tc.autoParameters()
        # use tuning curve defaults?
        manager.set_calibration_duration(winsz)
        # collect response
        manager.set_queue_callback('average_response', self.collect_avg_resp)
        manager.start_listening()
        self.results = []
        t = manager.run_calibration(0.1, False)
        t.join()
        manager.stop_listening()
        
        # calname = manager.process_calibration(False)
        fname = manager.datafile.filename
        manager.close_data()

        assert len(self.results) == ntraces * nreps

        # tone calibration should never save -- datafile is deleted on close if empty
        assert not os.path.isfile(fname)

    def collect_avg_resp(self, f, db, resultdb):
        self.results.append((f, db, resultdb))

    def test_noise_calibration_protocol(self):
        winsz = 0.1 #seconds
        manager, fname = self.create_acqmodel(winsz)
        acq_rate = manager.calibration_genrate()
        manager.set(caldb=66, calf=1234)
        manager.set_mphone_calibration(0.004, 94)

        manager.set_calibration_by_index(1)
        tc = manager.calibration_stimulus('noise')
        nreps = tc.repCount()
        # tc.autoParameters()
        # use tuning curve defaults?
        manager.set_calibration_duration(winsz)
        t = manager.run_calibration(0.1, False)
        t.join()
        calname, db = manager.process_calibration()
        fname = manager.datafile.filename
        manager.close_data()

        # now check saved data
        # print 'calname', calname
        hfile = h5py.File(fname, 'r')
        signals = hfile[calname]['signal']

        stim = json.loads(signals.attrs['stim'])
        cal_vector = hfile[calname]['calibration_intensities']

        assert_in('components', stim[0])
        # assert_equal(stim[0]['samplerate_da'], tc.samplerate())
        assert len(stim) == 1
        assert stim[0]['samplerate_da'] == tc.samplerate() == acq_rate == hfile[calname].attrs['samplerate_ad']
        npts =  winsz*acq_rate
        assert_equal(signals.shape,(nreps, npts))
        assert len(stim[0]['components']) == 1
        tone = stim[0]['components'][0]
        print tone['stim_type']
        assert tone['stim_type'] == 'FM Sweep'


        assert cal_vector.shape == ((npts/2+1),)

        reftone = hfile[calname]['reference_tone']
        # print 'reftone', reftone.attrs.keys()
        stim = json.loads(reftone.attrs['stim'])
        tone = stim[0]['components'][0]
        assert tone['stim_type'] == 'Pure Tone'
        assert tone['frequency'] == 1234
        assert tone['intensity'] == 66

        hfile.close()

    def test_correct_data_groups_created_protocol(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        self.fake_calibration(manager)

        #insert some stimuli
        tone0 = PureTone()
        tone0.setDuration(0.02)
        stim0 = StimulusModel()
        stim0.insertComponent(tone0)
        manager.protocol_model().insert(stim0,0)
        gen_rate = stim0.samplerate()

        # two calls to setup should not leave and empty group
        manager.setup_protocol(0.1)
        manager.setup_protocol(0.1)
        t = manager.run_protocol()
        t.join()

        manager.close_data()

        # now check saved data
        hfile = h5py.File(os.path.join(self.tempfolder, fname))
        groups = hfile.keys()
        assert 'segment_1' in groups
        assert 'segment_2' not in groups

        test = hfile['segment_1']['test_1']

        check_result(test, stim0, winsz, acq_rate)

        assert 'calibration_' in hfile['segment_1'].attrs['calibration_used'] 

        hfile.close()

    def test_mphone_calibration(self):
        winsz = 0.2 #seconds
        acq_rate = 50000
        manager, fname = self.create_acqmodel(winsz, acq_rate)
        t = manager.run_mphone_calibration(300)
        t.join()
        calval = manager.process_mphone_calibration()
        assert calval > 0

        manager.close_data()

    def create_acqmodel(self, winsz, acq_rate=None):
        manager = AcquisitionManager()
        fname = os.path.join(self.tempfolder, 'testdata' +rand_id()+ '.hdf5')
        manager.load_data_file(fname, 'w-')
        if acq_rate is None:
            acq_rate = manager.calibration_genrate()
        manager.set(aochan=u"PCI-6259/ao0", aichan=[u"PCI-6259/ai0"],
                           acqtime=winsz, aifs=acq_rate, caldb=100,
                           calv=1.0)
        return manager, fname

    def fake_calibration(self, manager):
        # cheat and pretend we already did a calibration
        frange = [5000, 100000]
        cal_data_file = open_acqdata(sample.calibration_filename(), filemode='r')
        calname = cal_data_file.calibration_list()[0]
        calibration_vector, calibration_freqs = cal_data_file.get_calibration(calname, reffreq=15000)
        cal_data_file.close()
        
        manager.explorer.set_calibration(calibration_vector, calibration_freqs, frange, calname)
        manager.protocoler.set_calibration(calibration_vector, calibration_freqs, frange, calname)
        manager.charter.set_calibration(calibration_vector, calibration_freqs, frange, calname)
        manager.bs_calibrator.stash_calibration(calibration_vector, calibration_freqs, frange, calname)
        manager.tone_calibrator.stash_calibration(calibration_vector, calibration_freqs, frange, calname)

def check_result(test_data, test_stim, winsz, acq_rate, nchans=1):
    ntraces = test_stim.traceCount()+1
    nreps = test_stim.repCount()
    stim_doc = json.loads(test_data.attrs['stim'])

    # print 'test_data', test_data, test_data.shape
    # print 'stim doc', stim_doc[0]

    # check everthing we can here
    assert test_data.attrs['user_tag'] == ''
    assert test_data.attrs['reps'] == nreps
    assert test_data.attrs['calv'] == test_stim.calv
    assert test_data.attrs['caldb'] == test_stim.caldb
    t = test_stim.stimType()
    if t is None: t = ''
    assert test_data.attrs['testtype'] == t
    
    assert_equal(test_data.shape,(ntraces, nreps, nchans, winsz*acq_rate))

    for stim_info in stim_doc:
        assert len(stim_info['time_stamps']) == test_data.attrs['reps']
        assert stim_info['overloaded_attenuation'] == 0
        assert stim_info['samplerate_da'] == test_stim.samplerate()
        for component_info in stim_info['components']:
            # required fields
            assert 'risefall' in component_info
            assert 'stim_type' in component_info
            assert 'intensity' in component_info
            assert 'duration' in component_info


    stim_doc = stim_doc[1:] # remove control stim
    # print stim_doc
    # to keep these tests simple, assume the altered component is at 
    # index 0,0 and there is only a single auto parameter
    if len(test_stim.autoParams().allData()) > 0:
        params = test_stim.autoParams().allData()
        value_ranges = test_stim.autoParamRanges()
        # print 'params', params, 'value_ranges', value_ranges
        if test_stim.reorder is None:
            for istim, stim_info in enumerate(stim_doc):
                prevlen = 1
                # make sure the right number of components
                assert len(stim_info['components']) == test_stim.componentCount()
                for ip, param in enumerate(params):
                    # print 'istim, ip', istim, ip, len(value_ranges[ip]), (istim / prevlen )% len(value_ranges[ip])
                    # print 'comparision', stim_info['components'][0][param['parameter']], value_ranges[ip][(istim / prevlen )% len(value_ranges[ip])]
                    assert stim_info['components'][0][param['parameter']] == value_ranges[ip][(istim / prevlen )% len(value_ranges[ip])]
                    prevlen *= len(value_ranges[ip])
        else:
            # just make sure the correct values are present
            for ip, param in enumerate(params):
                param_info = set([ stim_info['components'][0][param['parameter']] for stim_info in stim_doc])
                # print 'comparision', param_info , set(value_ranges[ip])
                assert param_info == set(value_ranges[ip])


def create_tone_stim(nreps):
    component = PureTone()
    stim_model = StimulusModel()
    stim_model.insertComponent(component, 0,0)
    stim_model.setRepCount(nreps)
    auto_model = stim_model.autoParams()
    auto_model.insertRow(0)
    
    auto_model.toggleSelection(0,component)

    # values = ['frequency', 0, 100, 10]
    values = ['duration', 0.065, 0.165, 0.010] # had caused problem in past
    auto_model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])

    return stim_model

def create_vocal_stim(nreps):
    component = Vocalization()
    component.setFile(sample.samplewav())
    delay = Silence()
    stim_model = StimulusModel()
    stim_model.insertComponent(delay, 0,0)
    stim_model.insertComponent(component, 0,0)
    stim_model.setRepCount(nreps)

    auto_model = stim_model.autoParams()
    auto_model.insertRow(0)
    p = {'parameter' : 'filename',
         'names' : [sample.samplewav(), sample.samplewav()],
         'selection' : []
        }
    auto_model.overwriteParam(0,p)
    auto_model.toggleSelection(0,component)

    return stim_model
