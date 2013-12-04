from nose.tools import raises

from spikeylab.stim.stimulusmodel import StimulusModel, PureTone
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
