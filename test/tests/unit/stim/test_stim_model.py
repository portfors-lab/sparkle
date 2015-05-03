import os

import numpy as np
import yaml
from nose.tools import assert_equal, raises

import test.sample as sample
from sparkle.data.open import open_acqdata
from sparkle.gui.stim.factory import CCFactory, TCFactory
from sparkle.gui.stim.stimulus_editor import StimulusEditor
from sparkle.stim.auto_parameter_model import AutoParameterModel
from sparkle.stim.reorder import order_function
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import PureTone, Vocalization, SquareWave
from sparkle.tools.systools import get_src_directory

src_dir = get_src_directory()
with open(os.path.join(src_dir,'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
USE_RMS = config['use_rms']
DEFAULT_SAMPLERATE = config['default_genrate']
MAXV = 1.5
DEVICE_MAXV = 10.0

class TestStimModel():
    def setup(self):
        self.model = StimulusModel()
        self.model.setReferenceVoltage(100, 0.1)
        self.model.setMaxVoltage(MAXV, DEVICE_MAXV)
        self.model.setMinVoltage(0.005)

    def test_insert_data(self):
        fake_component0 = 'ducks'
        fake_component1 = 'frogs'
        self.model.insertComponent(fake_component0, 0, 0)
        self.model.insertComponent(fake_component1, 0, 0)
        assert self.model.component(0,0) == fake_component1
        assert self.model.component(0,1) == fake_component0

    def test_remove_data(self):
        fake_component0 = 'ducks'
        self.model.insertComponent(fake_component0, 0, 0)
        self.model.removeComponent(0,0)
        assert self.model.component(0,0) == None

    def test_component_index(self):
        fake_component0 = 'ducks'
        # component will be added to the lowest index in row
        self.model.insertComponent(fake_component0, 0, 2)
        index = self.model.indexByComponent(fake_component0)
        assert index == (0,0)

    @raises(IndexError)
    def test_set_data(self):
        fake_component0 = 'ducks'
        self.model.overwriteComponent(fake_component0, 0, 0)

    def test_row_column_count(self):
        fake_component0 = 'ducks'
        self.model.insertComponent(fake_component0, 0, 0)
        assert self.model.columnCountForRow(0) == 1
        assert self.model.rowCount() == 1

    def test_trace_count_no_auto(self):
        component0 = PureTone()
        component1 = PureTone()
        self.model.insertComponent(component0, 0,0)
        self.model.insertComponent(component1, 0,0)

        assert self.model.traceCount() == 1

    def test_trace_count_no_components(self):
        self.add_auto_param(self.model)        

        assert self.model.traceCount() == 0

    def test_trace_count_with_auto(self):
        component = PureTone()
        self.model.insertComponent(component, 0,0)     

        nsteps = self.add_auto_param(self.model)        

        assert self.model.traceCount() == nsteps

    def test_model_contains(self):
        component = PureTone()
        self.model.insertComponent(component, 0,0)

        assert self.model.contains('PureTone')

    def test_expanded_stim_no_auto(self):
        """signal of a model without any auto parameters"""
        component = PureTone()
        self.model.insertComponent(component, 0,0)

        signals, doc, ovld = self.model.expandedStim()
        assert len(signals) == 1
        assert_equal(signals[0][0].shape[0], component.duration()*self.model.samplerate())
        assert len(doc) == 1
        assert doc[0]['samplerate_da'] == self.model.samplerate()

    def test_expanded_stim_with_auto(self):
        component = PureTone()
        self.model.insertComponent(component, 0,0)       
        nsteps = self.add_auto_param(self.model)        

        signals, doc, ovld = self.model.expandedStim()
        assert len(signals) == nsteps
        assert len(doc) == nsteps
        assert doc[0]['samplerate_da'] == self.model.samplerate()

    def test_expaned_stim_with_vocal_auto(self):
        component = Vocalization()
        component.setFile(sample.samplewav())
        self.model.insertComponent(component, 0,0)       
        nsteps = self.add_vocal_param(self.model)        

        signals, doc, ovld = self.model.expandedStim()
        assert len(signals) == nsteps
        assert len(doc) == nsteps
        assert doc[0]['samplerate_da'] == self.model.samplerate()

    def test_signal_eq_caldb(self):
        caldb = 100
        calv = 0.1
        component0 = PureTone()
        component1 = PureTone()
        component0.setIntensity(caldb)
        component1.setIntensity(80)
        self.model.insertComponent(component0, 0, 0)
        self.model.insertComponent(component1, 0, 0)
        self.model.setReferenceVoltage(caldb, calv)

        signal, atten, ovld = self.model.signal()
        assert atten == 0
        # rounding errors (or rather how python stores numbers) make this necessary
        if USE_RMS:
            print 'values', round(np.amax(signal),4), calv*1.414
            assert round(np.amax(signal),4) == calv*1.414
        else:
            assert round(np.amax(signal),3) == calv

    def test_signal_lt_caldb(self):
        caldb = 100
        calv = 0.1
        component0 = PureTone()
        component1 = PureTone()
        component0.setIntensity(caldb-20)
        component1.setIntensity(70)
        self.model.insertComponent(component0, 0,0)
        self.model.insertComponent(component1, 0,0)
        self.model.setReferenceVoltage(caldb, calv)

        signal, atten, ovld = self.model.signal()
        assert atten == 0
        # 20 decibel reduction == 0.1 scale in amplitude
        if USE_RMS:
            assert round(np.amax(signal),5) == (calv*1.414)/10
        else:
            assert round(np.amax(signal),4) == calv/10

    def test_signal_gt_caldb(self):
        caldb = 100
        calv = 0.1
        mod = 20
        component0 = PureTone()
        component1 = PureTone()
        component0.setIntensity(caldb+mod)
        component1.setIntensity(80)
        self.model.insertComponent(component0, 0,0)
        self.model.insertComponent(component1, 0,0)
        self.model.setReferenceVoltage(caldb, calv)

        signal, atten, ovld = self.model.signal()

        assert atten == 0
        # 20 decibel increase == 10x scale in amplitude
        if USE_RMS:
            print 'values', round(np.amax(signal),5), calv*1.414*10
            assert round(np.amax(signal),3) == (calv*1.414)*10
        else:
            assert round(np.amax(signal),4) == calv*10

    def test_signal_below_min(self):
        caldb = 100
        calv = 0.1
        minv = 0.005
        component0 = PureTone()
        component0.setIntensity(10)
        self.model.insertComponent(component0, 0,0)
        self.model.setMinVoltage(minv)        

        signal, atten, ovld = self.model.signal()
        assert atten > 0

        assert round(np.amax(signal),4) == minv

    def test_signal_with_zero_min(self):
        caldb = 100
        calv = 0.1
        component0 = PureTone()
        component0.setIntensity(10)
        self.model.setMinVoltage(0.0)
        self.model.insertComponent(component0, 0,0)
        self.model.setReferenceVoltage(caldb, calv)

        signal, atten, ovld = self.model.signal()
        assert atten == 0

        print 'max', np.amax(signal)
        assert np.amax(signal) > 0


    def test_signal_overload_voltage(self):
        caldb = 100
        calv = 12.0
        component0 = PureTone()
        component1 = PureTone()
        component0.setIntensity(caldb)
        component1.setIntensity(caldb)
        self.model.insertComponent(component0, 0, 0)
        self.model.insertComponent(component1, 1, 0)
        self.model.setReferenceVoltage(caldb, calv)

        signal, atten, ovld = self.model.signal()
        assert atten == 0
        print 'maxv', MAXV, 'signal max', np.amax(signal), 'overload', ovld
        assert round(np.amax(signal),2) == MAXV
        # do math to make this more accurate
        assert ovld > 0

    def test_square_wave_overload_voltage(self):
        component0 = SquareWave()
        component0.set('amplitude', 11.)
        self.model.insertComponent(component0, 0, 0)

        signal, atten, ovld = self.model.signal()
        assert atten == 0
        print 'maxv', DEVICE_MAXV, 'signal max', np.amax(signal), 'overload', ovld
        assert round(np.amax(signal),2) == DEVICE_MAXV
        # do math to make this more accurate
        assert ovld > 0

    def test_corrent_number_of_traces(self):
        self.model = self.stim_with_double_auto()
        n = self.model.traceCount()
        sig, doc, over = self.model.expandedStim()
        assert len(sig) == n

    def test_template_no_auto_params(self):
        self.model.setRepCount(7)
        component = PureTone()
        component.setIntensity(34)
        self.model.insertComponent(component, 0,0)
        vocal = Vocalization()
        vocal.setFile(sample.samplewav())
        self.model.insertComponent(vocal, 1,0)

        template = self.model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signal0, atten0, ovld = clone.signal()
        signal1, atten1, ovld = self.model.signal()

        assert clone.stimid != self.model.stimid
        np.testing.assert_array_equal(signal0, signal1)
        assert atten0 == atten1
        assert clone.repCount() == self.model.repCount()

    def test_template_with_auto_params(self):
        self.model.setRepCount(7)
        component = PureTone()
        component.setIntensity(34)
        self.model.insertComponent(component, 0,0)
        nsteps = self.add_auto_param(self.model) 

        template = self.model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0, ovld = self.model.expandedStim()
        signals1, docs1, ovld = clone.expandedStim()

        assert clone.stimid != self.model.stimid
        assert len(signals0) == len(signals1)
        for i in range(len(signals0)):
            signal0, atten0 = signals0[i]
            signal1, atten1 = signals1[i]
            np.testing.assert_array_equal(signal0, signal1)
            assert atten0 == atten1
            assert_equal(docs0[i], docs1[i])

        assert clone.repCount() == self.model.repCount()

    def test_template_with_auto_params_vocal(self):
        model = self.stim_with_double_auto()

        template = model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0, ovld = model.expandedStim()
        signals1, docs1, ovld = clone.expandedStim()

        assert clone.stimid != model.stimid
        assert len(signals0) == len(signals1)
        for i in range(len(signals0)):
            signal0, atten0 = signals0[i]
            signal1, atten1 = signals1[i]
            np.testing.assert_array_equal(signal0, signal1)
            assert atten0 == atten1
            assert_equal(docs0[i], docs1[i])

        assert clone.repCount() == model.repCount()

    def test_template_with_auto_params_randomized(self):
        self.model.setRepCount(7)
        component = PureTone()
        component.setIntensity(34)
        self.model.insertComponent(component, 0,0)
        nsteps = self.add_auto_param(self.model) 
        self.model.setReorderFunc(order_function('random'), 'random')

        template = self.model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0, ovld = self.model.expandedStim()
        signals1, docs1, ovld = clone.expandedStim()

        assert clone.stimid != self.model.stimid
        assert len(signals0) == len(signals1)
        assert clone.reorderName == self.model.reorderName
        # how to check if signal sets are the same?

        assert clone.repCount() == self.model.repCount()

    def test_template_tuning_curve(self):
        tcf = TCFactory()
        model = tcf.create()
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)

        template = model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0, ovld = model.expandedStim()
        signals1, docs1, ovld = clone.expandedStim()

        assert clone.stimid != model.stimid
        assert len(signals0) == len(signals1)
        assert clone.repCount() == model.repCount()
        for i in range(len(signals0)):
            print 'comparing signal', i
            signal0, atten0 = signals0[i]
            signal1, atten1 = signals1[i]
            np.testing.assert_array_equal(signal0, signal1)
            assert atten0 == atten1
            assert_equal(docs0[i], docs1[i])

    def test_calibration_template(self):
        ccf = CCFactory()
        model = ccf.create()
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)

        template = model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0, ovld = model.expandedStim()
        signals1, docs1, ovld = clone.expandedStim()

        assert clone.stimid != model.stimid
        assert len(signals0) == len(signals1)
        assert clone.repCount() == model.repCount()
        for i in range(len(signals0)):
            print 'comparing signal', i
            signal0, atten0 = signals0[i]
            signal1, atten1 = signals1[i]
            np.testing.assert_array_equal(signal0, signal1)
            print 'atten0 {}, atten1 {}'.format(atten0, atten1)
            assert atten0 == atten1
            assert_equal(docs0[i], docs1[i])

    def test_verify_no_components(self):
        assert self.model.verify()

    def test_verify_no_ref_voltage(self):
        self.model.setReferenceVoltage(None, None)
        component = PureTone()
        self.model.insertComponent(component, 0,0)

        assert self.model.verify()

    def test_verify_conflicting_samplerates(self):
        component = Vocalization()
        component.setFile(sample.samplewav())
        self.model.insertComponent(component)
        component = Vocalization()
        component.setFile(sample.samplewav333())
        self.model.insertComponent(component)

        assert 'conflicting samplerate' in self.model.verify()

    def test_verify_short_duration(self):

        component = PureTone()
        component.setDuration(0.003)
        component.setRisefall(0.004)
        self.model.insertComponent(component, 0,0)
        
        invalid = self.model.verify()
        print 'msg', invalid
        assert invalid

    def test_verify_long_duration(self):
        component = PureTone()
        component.setDuration(0.3)
        self.model.insertComponent(component, 0,0)
        
        assert self.model.verify(windowSize=0.2)


    def test_verify_success(self):
        component = PureTone()
        self.model.insertComponent(component, 0,0)
        
        assert self.model.verify() == 0

    def test_verify_success_with_autoparameters(self):
        component = PureTone()
        component.setRisefall(0.003)
        self.model.insertComponent(component, 0,0)

        ap_model = self.model.autoParams()
        ap_model.insertRow(0)
        ap_model.toggleSelection(0, component)

        # values are in seconds
        values = ['duration', 0.020, 0.008, 0.001]
        ap_model.setParamValue(0, parameter=values[0], start=values[1],
                               stop=values[2], step=values[3])

        invalid = self.model.verify(windowSize=0.1)
        print 'msg', invalid
        assert invalid == 0

    def test_verify_parameter_conflict(self):
        """When a combination of paramters in auto-parameters causes
        a conflict"""
        component = PureTone()
        component.setRisefall(0.005)
        self.model.insertComponent(component, 0,0)

        ap_model = self.model.autoParams()
        ap_model.insertRow(0)
        ap_model.toggleSelection(0, component)
        
        values = ['duration', 0.020, 0.004, 0.001]
        ap_model.setParamValue(0, parameter=values[0], start=values[1],
                               stop=values[2], step=values[3])

        invalid = self.model.verify()
        print 'msg', invalid
        assert invalid

    def test_verify_with_long_auto_parameter(self):
        component = PureTone()
        self.model.insertComponent(component, 0,0)

        ap_model = self.model.autoParams()
        ap_model.insertRow(0)
        ap_model.toggleSelection(0, component)

        # default value is in ms
        values = ['duration', 0.050, 0.200, 0.025]
        ap_model.setParamValue(0, parameter=values[0], start=values[1],
                               stop=values[2], step=values[3])

        invalid = self.model.verify(windowSize=0.1)
        print 'msg', invalid
        assert invalid

    def test_calibration_samplerates_change(self):
        # get some calibration data
        frange = [5000, 100000]
        cal_data_file = open_acqdata(sample.calibration_filename(), filemode='r')
        calname = cal_data_file.calibration_list()[0]
        calibration_vector, calibration_freqs = cal_data_file.get_calibration(calname, reffreq=15000)

        assert self.model.impulseResponse is None
        self.model.setCalibration(calibration_vector, calibration_freqs, frange)
        assert self.model.impulseResponse is not None

        component = PureTone()

        self.model.insertComponent(component, 0,0)
        print self.model._calibration_fs, DEFAULT_SAMPLERATE
        assert self.model._calibration_fs == DEFAULT_SAMPLERATE

        component = Vocalization()
        component.setFile(sample.samplewav())
        self.model.insertComponent(component)

        assert self.model._calibration_fs == component.samplerate()

        self.model.removeComponent(0,0)

        assert self.model._calibration_fs == DEFAULT_SAMPLERATE

    def add_auto_param(self, model):
        # adds an autoparameter to the given model
        ptype = 'intensity'
        start = 0
        step = 1
        stop = 3

        parameter_model = model.autoParams()
        parameter_model.insertRow(0)
        # select first component
        parameter_model.toggleSelection(0, model.component(0,0))
        # set values for autoparams
        parameter_model.setParamValue(0, start=start, step=step, 
                                      stop=stop, parameter=ptype)

        return len(range(start,stop,step)) + 1

    def add_vocal_param(self, model):
        p = {'parameter' : 'filename',
                'names' : [sample.samplewav(), sample.samplewav()],
                'selection' : []
        }
        parameter_model = model.autoParams()
        parameter_model.insertRow(0)
        parameter_model.overwriteParam(0,p)
        # select first component
        parameter_model.toggleSelection(0, model.component(0,0))

        return parameter_model.numSteps(0)

    def stim_with_double_auto(self):
        model = StimulusModel()
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)
        component = Vocalization()
        component.setFile(sample.samplewav())
        model.insertComponent(component, 0,0)
        nsteps0 = self.add_vocal_param(model) 
        nsteps1 = self.add_auto_param(model)
        nsteps = nsteps0*nsteps1

        return model