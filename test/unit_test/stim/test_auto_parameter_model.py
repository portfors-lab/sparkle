from nose.tools import assert_in

from spikeylab.stim.auto_parameter_model import AutoParameterModel

class TestAutoParameterModel():
    def test_insert_rows(self):
        param_model = AutoParameterModel()
        param_model.insertRows(0, 1)

        param = param_model.data(param_model.index(0))
        assert param_model.rowCount() == 1
        for item in ['start', 'stop', 'delta', 'parameter']:
            assert_in(item, param)

    def test_remove_rows(self):
        model = AutoParameterModel()
        model.insertRows(0, 1)
        model.removeRows(0, 1)
        assert model.rowCount() == 0
