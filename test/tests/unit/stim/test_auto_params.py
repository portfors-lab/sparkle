from nose.tools import assert_in

import test.sample as sample
from sparkle.stim.abstract_component import AbstractStimulusComponent
from sparkle.stim.auto_parameter_model import AutoParameterModel
from sparkle.stim.types.stimuli_classes import PureTone, Vocalization


class TestAutoParameterModel():
    def test_insert_rows(self):
        param_model = AutoParameterModel()
        param_model.insertRow(0)

        param = param_model.param(0)
        assert param_model.nrows() == 1
        for item in ['start', 'stop', 'step', 'parameter']:
            assert_in(item, param)

    def test_remove_rows(self):
        model = AutoParameterModel()
        model.insertRow(0)
        model.removeRow(0)
        assert model.nrows() == 0

    def test_get_detail_empty_selection(self):
        model = AutoParameterModel()
        model.insertRow(0)
        label = model.getDetail(0, 'label')
        assert label == None

    def test_get_detail_with_selection(self):
        # need to create a stimulus model with component for this to work
        component = PureTone()
        model = self.create_model(component)

        parameter = 'frequency'
        model.setParamValue(0, parameter=parameter)

        details = ['unit', 'min', 'max']
        for detail in details:
            d = model.getDetail(0, detail)
            assert d == component.auto_details()[parameter][detail]

    def test_data(self):
        component = PureTone()
        model = self.create_model(component)

        values = ['frequency', 0, 100000, 10000]
        model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])
        
        # just get them back to make sure they are set correctly
        assert values[0] == model.paramValue(0, 'parameter')
        assert values[1] == model.paramValue(0, 'start')
        assert values[2] == model.paramValue(0, 'stop')
        assert values[3] == model.paramValue(0, 'step')

    def test_verify_success_with_perfect_autoparameter_spacing(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['duration', 0.008, 0.0980, 0.010]
        model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])

        assert model.verify() == 0
        assert model.numSteps(0) == 10
        assert list(model.ranges()[0]) == [0.008, 0.018, 0.028, 0.038, 0.048, 0.058, 0.068, 0.078, 0.088, 0.098]

    def test_verify_success_with_non_perfect_autoparameter_spacing(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['duration', 0.008, 0.100, 0.010]
        model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])

        assert model.verify() == 0
        assert model.numSteps(0) == 11
        assert list(model.ranges()[0]) == [0.008, 0.018, 0.028, 0.038, 0.048, 0.058, 0.068, 0.078, 0.088, 0.098, 0.1]

    def test_verify_blank_inputs(self):
        component = PureTone()
        model = self.create_model(component)

        assert model.verify()

    def test_verify_bad_default_range(self):
        component = PureTone()
        model = self.create_model(component)
        model.setParamValue(0, parameter='duration')

        # duration 0 now allowed
        assert model.verify() == 0

    def test_verify_bad_step_size(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['duration', 0.008, 0.100]
        model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2])

        assert model.verify()

    def test_verify_bad_range_ok_step_size(self):
        component = PureTone()
        model = self.create_model(component)
        model.setParamValue(0, parameter='duration', step=0.001)

        assert model.verify()

    def test_verify_bad_start_value(self):
        component = PureTone()
        model = self.create_model(component)
        model.setParamValue(0, parameter='duration', start=-0.001,
                            stop=0.01, step=0.001)

        assert model.verify()

    def test_verify_bad_stopstep_value(self):
        component = PureTone()
        model = self.create_model(component)

        model.setParamValue(0, parameter='duration', start = 0.01,
                            stop=0.01, step=0.01)

        assert model.verify()

    def test_verify_start_stop_equal_ok(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['intensity', 100, 100, 0]
        model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])

        assert model.verify() == 0

    def test_verify_incompatable_paramter(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['frequency', 5, 10, 2]
        model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])

        vcomponent = Vocalization()
        vcomponent.setFile(sample.samplewav())
        model.toggleSelection(0, vcomponent)

        assert 'frequency not present' in model.verify()

    def test_filename_parameter(self):
        component = Vocalization()
        model = AutoParameterModel()
        model.insertRow(0)
        p = {'parameter' : 'filename',
                'names' : ['file0', 'file1', 'file2'],
                'selection' : []
        }
        model.overwriteParam(0, p)
        model.toggleSelection(0, component)

        assert model.verify() == 0
        assert model.numSteps(0) == 3

    def test_ranges_odd(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['frequency', 5, 10, 2]
        model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])

        vcomponent = Vocalization()
        vcomponent.setFile(sample.samplewav())
        model.insertRow(1)
        p = {'parameter' : 'filename',
                'names' : [sample.samplewav()],
                'selection' : []
        }
        model.overwriteParam(1, p)
        model.toggleSelection(1, vcomponent)

        assert model.verify() == 0
        steps = model.ranges()
        print 'steps', steps
        assert list(steps[0]) == [5., 7., 9., 10.] 
        assert steps[1] == [sample.samplewav()] 

    def test_ranges_even(self):
        component = PureTone()
        model = self.create_model(component)
        values = ['frequency', 5, 9, 2]
        model.setParamValue(0, parameter=values[0], start=values[1], 
                            stop=values[2], step=values[3])

        assert model.verify() == 0
        steps = model.ranges()
        print 'steps', steps
        assert list(steps[0]) == [5., 7., 9.] 

    def create_model(self, component):
        model = AutoParameterModel()
        model.insertRow(0)
        
        model.toggleSelection(0, component)

        return model
