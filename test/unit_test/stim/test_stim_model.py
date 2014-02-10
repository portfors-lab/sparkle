from nose.tools import raises, assert_equal

import numpy as np

from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import PureTone
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from PyQt4 import QtCore, QtGui

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

    def test_verify_with_bad_frequency_auto_parameter(self):
        component = PureTone()
        stim_model = StimulusModel()
        stim_model.setReferenceVoltage(100, 0.1)
        stim_model.insertComponent(component, (0,0))
        stim_model.setSamplerate(375000)

        ap_model = stim_model.autoParams()
        ap_model.insertRows(0, 1)
        
        selection_model = ap_model.data(ap_model.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim_model.index(0,0))

        # default value is in kHz
        values = ['frequency', 50, 200, 25]
        for i, value in enumerate(values):
            ap_model.setData(ap_model.index(0,i), value, QtCore.Qt.EditRole)

        invalid = stim_model.verify(window_size=0.1)
        print 'msg', invalid
        assert invalid
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


        