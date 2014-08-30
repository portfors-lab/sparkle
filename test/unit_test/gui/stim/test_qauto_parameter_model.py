from nose.tools import assert_in

from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.gui.stim.qauto_parameter_model import QAutoParameterModel
from spikeylab.stim.abstract_stimulus import AbstractStimulusComponent
from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization

from PyQt4 import QtCore

import test.sample as sample

class TestAutoParameterModel():
    def setUp(self):
        self.original_tunits = AbstractStimulusComponent._scales[0]
        self.original_funits = AbstractStimulusComponent._scales[1]

    def tearDown(self):
        AbstractStimulusComponent().update_tscale(self.original_tunits)
        AbstractStimulusComponent().update_fscale(self.original_funits)

    def test_insert_rows(self):
        data = AutoParameterModel()
        param_model = QAutoParameterModel(data)
        param_model.insertRows(0, 1)

        param = param_model.data(param_model.index(0,0))
        assert param_model.rowCount() == 1
        for item in ['start', 'stop', 'step', 'parameter']:
            assert_in(item, param)

    def test_remove_rows(self):
        data = AutoParameterModel()
        model = QAutoParameterModel(data)
        model.insertRows(0, 1)
        model.removeRows(0, 1)
        assert model.rowCount() == 0

    def test_data(self):
        component = PureTone()
        model = self.create_model(component)

        values = ['frequency', 0, 100, 10]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        # just get them back to make sure they are set correctly
        for i, value in enumerate(values):
            assert value == model.data(model.index(0,i), QtCore.Qt.EditRole)

    def test_file_item(self):
        model = self.create_model_vocal()

        param = model.data(model.index(0,0))
        assert param['names'] == [sample.samplewav()]

    def test_data_out_of_range(self):
        component = PureTone()
        model = self.create_model(component)

        details = component.auto_details()
        original_start = model.data(model.index(0,1))
        original_stop = model.data(model.index(0,2))

        parameter = 'frequency'
        values = [parameter, details[parameter]['min']-1, details[parameter]['max']+1, 10]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        assert original_start == model.data(model.index(0,1))
        assert original_stop == model.data(model.index(0,2))

    def test_units_change_frequency(self):
        component = PureTone()
        model = self.create_model(component)

        values = ['frequency', 0, 100, 10]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        details = component.auto_details()
        multiplier = details[values[0]]['multiplier']

        unit0 = details[values[0]]['label']
        nsteps0 = model.data(model.index(0,4), QtCore.Qt.EditRole)
        assert model.data(model.index(0,1), QtCore.Qt.ToolTipRole) == unit0

        AbstractStimulusComponent().update_fscale(1)
        
        details = component.auto_details()
        unit1 = details[values[0]]['label']
        assert unit0 != unit1
        assert model.data(model.index(0,1), QtCore.Qt.ToolTipRole) == unit1

        assert values[1]*multiplier == model.data(model.index(0,1), QtCore.Qt.EditRole)
        assert values[2]*multiplier == model.data(model.index(0,2), QtCore.Qt.EditRole)
        assert values[3]*multiplier == model.data(model.index(0,3), QtCore.Qt.EditRole)
        assert nsteps0 == model.data(model.index(0,4), QtCore.Qt.EditRole)

    def test_units_change_time(self):
        component = PureTone()
        model = self.create_model(component)

        values = ['duration', 5, 100, 10]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        details = component.auto_details()
        multiplier = details[values[0]]['multiplier']

        unit0 = details[values[0]]['label']
        nsteps0 = model.data(model.index(0,4), QtCore.Qt.EditRole)
        assert model.data(model.index(0,1), QtCore.Qt.ToolTipRole) == unit0

        AbstractStimulusComponent().update_tscale(1)
        
        details = component.auto_details()
        unit1 = details[values[0]]['label']
        assert unit0 != unit1
        assert model.data(model.index(0,1), QtCore.Qt.ToolTipRole) == unit1

        assert values[1]*multiplier == model.data(model.index(0,1), QtCore.Qt.EditRole)
        print 'multiplier', multiplier*values[2],  model.data(model.index(0,2), QtCore.Qt.EditRole)
        assert values[2]*multiplier == model.data(model.index(0,2), QtCore.Qt.EditRole)
        assert values[3]*multiplier == model.data(model.index(0,3), QtCore.Qt.EditRole)
        assert nsteps0 == model.data(model.index(0,4), QtCore.Qt.EditRole)

    def test_change_param_type(self):
        component = PureTone()
        model = self.create_model(component)

        values = ['duration', 8, 100, 10]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        # check that values are stored correctly inside model
        p = model.data(model.index(0,0))
        mult = model.model.getDetail(0, 'multiplier')
        for i, value in enumerate(values[1:]):
            assert p[model.headerData(i+1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)] == value*mult

        values[0] = 'frequency'
        model.setData(model.index(0,0), 'frequency', QtCore.Qt.EditRole)
        for i, value in enumerate(values):
            assert model.data(model.index(0,i), QtCore.Qt.EditRole) == value

        # check that values are stored correctly inside model
        p = model.data(model.index(0,0))
        mult = model.model.getDetail(0, 'multiplier')
        for i, value in enumerate(values[1:]):
            assert p[model.headerData(i+1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)] == value*mult

    def test_verify_success(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['duration', 8, 100, 10]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        assert model.verify() == 0

    def test_verify_blank_inputs(self):
        component = PureTone()
        model = self.create_model(component)

        assert model.verify()

    def test_verify_bad_default_range(self):
        component = PureTone()
        model = self.create_model(component)
        model.setData(model.index(0,0), 'duration', QtCore.Qt.EditRole)

        # duration 0 now allowed
        assert model.verify() == 0

    def test_verify_bad_step_size(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['duration', 8, 100]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        assert model.verify()

    def test_verify_bad_range_ok_step_size(self):
        component = PureTone()
        model = self.create_model(component)
        model.setData(model.index(0,0), 'duration', QtCore.Qt.EditRole)
        model.setData(model.index(0,3), 1, QtCore.Qt.EditRole)

        assert model.verify()

    def test_verify_bad_start_value(self):
        component = PureTone()
        model = self.create_model(component)
        model.setData(model.index(0,0), 'duration', QtCore.Qt.EditRole)
        model.setData(model.index(0,1), -1, QtCore.Qt.EditRole)
        model.setData(model.index(0,2), 10, QtCore.Qt.EditRole)
        model.setData(model.index(0,3), 1, QtCore.Qt.EditRole)

        # cannot set a bad start value
        assert model.verify() == 0

    def test_verify_bad_stopstep_value(self):
        component = PureTone()
        model = self.create_model(component)
        model.setData(model.index(0,0), 'duration', QtCore.Qt.EditRole)
        model.setData(model.index(0,1), 10, QtCore.Qt.EditRole)
        model.setData(model.index(0,2), 10, QtCore.Qt.EditRole)
        model.setData(model.index(0,3), 10, QtCore.Qt.EditRole)

        assert model.verify()

    def test_verify_start_stop_equal_ok(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['intensity', 100, 100, 0]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        assert model.verify() == 0

    def test_verify_incompatable_paramter(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['frequency', 5, 10, 2]
        for i, value in enumerate(values):
            model.setData(model.index(0,i), value, QtCore.Qt.EditRole)

        vcomponent = Vocalization()
        vcomponent.setFile(sample.samplewav())
        model.toggleSelection(model.index(0,0), vcomponent)

        assert 'frequency not present' in model.verify()

    def test_verify_with_vocal_success(self):
        model = self.create_model_vocal()
        assert model.verify() == 0

    def test_verify_with_vocal_no_selection(self):
        model = self.create_model_vocal()
        param = model.data(model.index(0,0))
        param['selection'] = []

        assert "At least one component" in model.verify()

    def create_model(self, component):
        model = AutoParameterModel()
        model.insertRow(0)
        
        model.toggleSelection(0, component)

        return QAutoParameterModel(model)

    def create_model_vocal(self):
        component = Vocalization()
        model = QAutoParameterModel(AutoParameterModel())

        p = {'parameter': 'file',
             'names': [sample.samplewav()],
             'selection': [component]
        }
        model.insertItem(model.index(0,0), p)
        return model