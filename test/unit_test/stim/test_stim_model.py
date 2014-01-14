from nose.tools import raises, assert_equal

from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import PureTone
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from PyQt4 import QtCore

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

        signals = model.expandedStim()
        assert len(signals) == 1
        assert_equal(signals[0][0].shape[0], component.duration()*model.samplerate())

    def test_expanded_stim_with_auto(self):
        model = StimulusModel()
        component = PureTone()
        model.insertComponent(component, (0,0))       

        nsteps = self.add_auto_param(model)        

        signals = model.expandedStim()
        assert len(signals) == nsteps

    def test_expanded_doc(self):
        model = StimulusModel()
        component = PureTone()
        model.insertComponent(component, (0,0))

        nsteps = self.add_auto_param(model)

        doc = model.expandedDoc()
        assert len(doc) == nsteps
        assert doc[0]['samplerate_da'] == model.samplerate()

    def add_auto_param(self, model):
        # adds an autoparameter to the given model
        start = 0
        step = 1
        stop = 3

        parameter_model = model.autoParams()
        parameter_model.insertRows(0,1)
        auto_parameter = parameter_model.data(parameter_model.index(0))
        auto_parameter['start'] = start
        auto_parameter['delta'] = step
        auto_parameter['stop'] = stop
        parameter_model.setData(parameter_model.index(0), auto_parameter)

        return len(range(start,stop,step))


        