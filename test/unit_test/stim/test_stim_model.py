from nose.tools import raises, assert_equal

import numpy as np

from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.stim.stimulus_editor import StimulusEditor
from spikeylab.stim.factory import TCFactory, CCFactory
from spikeylab.stim.reorder import order_function

from PyQt4 import QtCore, QtGui

import test.sample as sample

# get an error accessing class names if there is not a qapp running
app = None
def setUp():
    global app
    app = QtGui.QApplication([])

def tearDown():
    global app
    app.exit(0)

class TestStimModel():
    def test_insert_data(self):
        model = StimulusModel()
        fake_component0 = 'ducks'
        fake_component1 = 'frogs'
        model.insertComponent(fake_component0, (0,0))
        model.insertComponent(fake_component1, (0,0))
        assert model.data(model.index(0,0), role=QtCore.Qt.UserRole) == fake_component1
        assert model.data(model.index(0,1), role=QtCore.Qt.UserRole) == fake_component0

    def test_remove_data(self):
        model = StimulusModel()
        fake_component0 = 'ducks'
        model.insertComponent(fake_component0, (0,0))
        model.removeComponent((0,0))
        assert model.data(model.index(0,0), role=QtCore.Qt.UserRole) == None

    def test_component_index(self):
        model = StimulusModel()
        fake_component0 = 'ducks'
        # component will be added to the lowest index in row
        model.insertComponent(fake_component0, (0,2))
        index = model.indexByComponent(fake_component0)
        assert (index.row(),index.column()) == (0,0)

    @raises(IndexError)
    def test_set_data(self):
        model = StimulusModel()
        fake_component0 = 'ducks'
        model.setData(model.index(0,0), fake_component0)

    def test_column_count(self):
        model = StimulusModel()
        fake_component0 = 'ducks'
        model.insertComponent(fake_component0, (0,0))
        assert model.columnCountForRow(0) == 1

    def test_row_count(self):
        model = StimulusModel()
        fake_component0 = 'ducks'
        model.insertComponent(fake_component0, (0,0))
        # there is always an extra empty row
        assert model.rowCount() == 2

    def test_trace_count_no_auto(self):
        model = StimulusModel()
        component0 = PureTone()
        component1 = PureTone()
        model.insertComponent(component0, (0,0))
        model.insertComponent(component1, (0,0))

        assert model.traceCount() == 1

    def test_trace_count_no_components(self):
        model = StimulusModel()
        self.add_auto_param(model)        

        assert model.traceCount() == 0

    def test_trace_count_with_auto(self):
        model = StimulusModel()
        component = PureTone()
        model.insertComponent(component, (0,0))       

        nsteps = self.add_auto_param(model)        

        assert model.traceCount() == nsteps

    def test_model_contains(self):
        model = StimulusModel()
        component = PureTone()
        model.insertComponent(component, (0,0))

        assert model.contains('PureTone')

    def test_expanded_stim_no_auto(self):
        """signal of a model without any auto parameters"""
        model = StimulusModel()
        component = PureTone()
        model.insertComponent(component, (0,0))
        model.setReferenceVoltage(100, 0.1)

        signals, doc = model.expandedStim()
        assert len(signals) == 1
        assert_equal(signals[0][0].shape[0], component.duration()*model.samplerate())
        assert len(doc) == 1
        assert doc[0]['samplerate_da'] == model.samplerate()

    def test_expanded_stim_with_auto(self):
        model = StimulusModel()
        component = PureTone()
        model.insertComponent(component, (0,0))       
        model.setReferenceVoltage(100, 0.1)
        nsteps = self.add_auto_param(model)        

        signals, doc = model.expandedStim()
        assert len(signals) == nsteps
        assert len(doc) == nsteps
        assert doc[0]['samplerate_da'] == model.samplerate()

    def test_signal_eq_caldb(self):
        caldb = 100
        calv = 0.1
        model = StimulusModel()
        component0 = PureTone()
        component1 = PureTone()
        component0.setIntensity(caldb)
        component1.setIntensity(80)
        model.insertComponent(component0, (0,0))
        model.insertComponent(component1, (0,0))
        model.setReferenceVoltage(caldb, calv)

        signal, atten = model.signal()
        assert atten == 0
        # rounding errors (or rather how python stores numbers) make this necessary
        assert round(np.amax(signal),3) == calv

    def test_signal_lt_caldb(self):
        caldb = 100
        calv = 0.1
        model = StimulusModel()
        component0 = PureTone()
        component1 = PureTone()
        component0.setIntensity(caldb-10)
        component1.setIntensity(80)
        model.insertComponent(component0, (0,0))
        model.insertComponent(component1, (0,0))
        model.setReferenceVoltage(caldb, calv)

        signal, atten = model.signal()
        assert atten == 10
        assert round(np.amax(signal),3) == calv

    def test_signal_gt_caldb(self):
        caldb = 100
        calv = 0.1
        mod = 10
        model = StimulusModel()
        component0 = PureTone()
        component1 = PureTone()
        component0.setIntensity(caldb+mod)
        component1.setIntensity(80)
        model.insertComponent(component0, (0,0))
        model.insertComponent(component1, (0,0))
        model.setReferenceVoltage(caldb, calv)

        signal, atten = model.signal()
        assert atten == 0
        print 'recieved', np.amax(signal), 'expected', calv*(10 **(mod/20.))
        assert round(np.amax(signal),3) == round(calv*(10 **(mod/20.)),3)

    def test_template_no_auto_params(self):
        model = StimulusModel()
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)
        component = PureTone()
        component.setIntensity(34)
        model.insertComponent(component, (0,0))
        vocal = Vocalization()
        vocal.setFile(sample.samplewav())
        model.insertComponent(vocal, (1,0))

        template = model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signal0, atten0 = clone.signal()
        signal1, atten1 = model.signal()

        assert clone.stimid != model.stimid
        np.testing.assert_array_equal(signal0, signal1)
        assert atten0 == atten1
        assert clone.repCount() == model.repCount()

    def test_template_with_auto_params(self):
        model = StimulusModel()
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)
        component = PureTone()
        component.setIntensity(34)
        model.insertComponent(component, (0,0)) 
        nsteps = self.add_auto_param(model) 
        model.setEditor(StimulusEditor)

        template = model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0 = model.expandedStim()
        signals1, docs1 = clone.expandedStim()

        assert clone.stimid != model.stimid
        assert len(signals0) == len(signals1)
        assert clone.editor.name == model.editor.name
        for i in range(len(signals0)):
            signal0, atten0 = signals0[i]
            signal1, atten1 = signals1[i]
            np.testing.assert_array_equal(signal0, signal1)
            assert atten0 == atten1
            assert_equal(docs0[i], docs1[i])

        assert clone.repCount() == model.repCount()

    def test_template_with_auto_params_randomized(self):
        model = StimulusModel()
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)
        component = PureTone()
        component.setIntensity(34)
        model.insertComponent(component, (0,0)) 
        nsteps = self.add_auto_param(model) 
        model.setEditor(StimulusEditor)
        model.setReorderFunc(order_function('random'), 'random')

        template = model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0 = model.expandedStim()
        signals1, docs1 = clone.expandedStim()

        assert clone.stimid != model.stimid
        assert len(signals0) == len(signals1)
        assert clone.editor.name == model.editor.name
        assert clone.reorder_name == model.reorder_name
        # how to check if signal sets are the same?

        assert clone.repCount() == model.repCount()

    def test_template_tuning_curve(self):
        model = StimulusModel()
        tcf = TCFactory()
        tcf.init_stim(model)
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)
        model.setEditor(tcf.editor())

        template = model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0 = model.expandedStim()
        signals1, docs1 = clone.expandedStim()

        assert clone.stimid != model.stimid
        assert len(signals0) == len(signals1)
        assert clone.editor.name == model.editor.name
        assert clone.repCount() == model.repCount()
        for i in range(len(signals0)):
            print 'comparing signal', i
            signal0, atten0 = signals0[i]
            signal1, atten1 = signals1[i]
            np.testing.assert_array_equal(signal0, signal1)
            assert atten0 == atten1
            assert_equal(docs0[i], docs1[i])

    def test_calibration_template(self):
        model = StimulusModel()
        ccf = CCFactory()
        ccf.init_stim(model)
        model.setReferenceVoltage(100, 0.1)
        model.setRepCount(7)
        model.setEditor(ccf.editor())

        template = model.templateDoc()

        clone = StimulusModel.loadFromTemplate(template)
        clone.setReferenceVoltage(100, 0.1)

        signals0, docs0 = model.expandedStim()
        signals1, docs1 = clone.expandedStim()

        assert clone.stimid != model.stimid
        assert len(signals0) == len(signals1)
        assert clone.editor.name == model.editor.name
        assert clone.repCount() == model.repCount()
        for i in range(len(signals0)):
            print 'comparing signal', i
            signal0, atten0 = signals0[i]
            signal1, atten1 = signals1[i]
            np.testing.assert_array_equal(signal0, signal1)
            assert atten0 == atten1
            assert_equal(docs0[i], docs1[i])

    def test_verify_no_components(self):
        model = StimulusModel()
        model.setReferenceVoltage(100, 0.1)
        assert model.verify()

    def test_verify_no_ref_voltage(self):
        model = StimulusModel()
        component = PureTone()
        model.insertComponent(component, (0,0))
        
        assert model.verify()

    def test_verify_short_duration(self):

        model = StimulusModel()
        model.setReferenceVoltage(100, 0.1)
        component = PureTone()
        component.setDuration(0.003)
        component.setRisefall(0.002)
        model.insertComponent(component, (0,0))
        
        invalid = model.verify()
        print 'msg', invalid
        assert invalid

    def test_verify_long_duration(self):
        model = StimulusModel()
        model.setReferenceVoltage(100, 0.1)
        component = PureTone()
        component.setDuration(0.3)
        model.insertComponent(component, (0,0))
        
        assert model.verify(window_size=0.2)


    def test_verify_success(self):
        model = StimulusModel()
        model.setReferenceVoltage(100, 0.1)
        component = PureTone()
        model.insertComponent(component, (0,0))
        
        assert model.verify() == 0

    def test_verify_success_with_autoparameters(self):
        component = PureTone()
        component.setRisefall(0.003)
        stim_model = StimulusModel()
        stim_model.setReferenceVoltage(100, 0.1)
        stim_model.insertComponent(component, (0,0))

        ap_model = stim_model.autoParams()
        ap_model.insertRows(0, 1)
        
        selection_model = ap_model.data(ap_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim_model.index(0,0))

        # default value is in ms
        values = ['duration', 20, 8, 1]

        details = component.auto_details()
        multiplier = details[values[0]]['multiplier']
        unit0 = details[values[0]]['label']
        print 'multiplier', multiplier, unit0

        for i, value in enumerate(values):
            ap_model.setData(ap_model.index(0,i), value, QtCore.Qt.EditRole)

        invalid = stim_model.verify(window_size=0.1)
        print 'msg', invalid
        assert invalid == 0

    def test_verify_parameter_conflict(self):
        """When a combination of paramters in auto-parameters causes
        a conflict"""
        component = PureTone()
        component.setRisefall(0.005)
        stim_model = StimulusModel()
        stim_model.setReferenceVoltage(100, 0.1)
        stim_model.insertComponent(component, (0,0))

        ap_model = stim_model.autoParams()
        ap_model.insertRows(0, 1)
        
        selection_model = ap_model.data(ap_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim_model.index(0,0))

        values = ['duration', 20, 4, 1]
        for i, value in enumerate(values):
            ap_model.setData(ap_model.index(0,i), value, QtCore.Qt.EditRole)

        invalid = stim_model.verify()
        print 'msg', invalid
        assert invalid

    def test_verify_with_long_auto_parameter(self):
        component = PureTone()
        stim_model = StimulusModel()
        stim_model.setReferenceVoltage(100, 0.1)
        stim_model.insertComponent(component, (0,0))

        ap_model = stim_model.autoParams()
        ap_model.insertRows(0, 1)
        
        selection_model = ap_model.data(ap_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim_model.index(0,0))

        # default value is in ms
        values = ['duration', 50, 200, 25]

        for i, value in enumerate(values):
            ap_model.setData(ap_model.index(0,i), value, QtCore.Qt.EditRole)

        invalid = stim_model.verify(window_size=0.1)
        print 'msg', invalid
        assert invalid

    def test_verify_with_bad_frequency_auto_parameter_disallowed(self):
        component = PureTone()
        stim_model = StimulusModel()
        stim_model.setReferenceVoltage(100, 0.1)
        stim_model.insertComponent(component, (0,0))

        ap_model = stim_model.autoParams()
        ap_model.insertRows(0, 1)
        
        selection_model = ap_model.data(ap_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim_model.index(0,0))

        # default value is in kHz
        values = ['frequency', 100, 300, 25]
        for i, value in enumerate(values):
            ap_model.setData(ap_model.index(0,i), value, QtCore.Qt.EditRole)

        invalid = stim_model.verify(window_size=0.1)
        print 'msg', invalid
        assert invalid == 0
        assert stim_model.contains_pval('frequency', 75000)

    def add_auto_param(self, model):
        # adds an autoparameter to the given model
        start = 0
        step = 1
        stop = 3

        parameter_model = model.autoParams()
        parameter_model.insertRows(0,1)
        auto_parameter = parameter_model.data(parameter_model.index(0,0))
        auto_parameter['start'] = start
        auto_parameter['step'] = step
        auto_parameter['stop'] = stop
        parameter_model.setData(parameter_model.index(0,0), auto_parameter)

        return len(range(start,stop,step)) + 1


        