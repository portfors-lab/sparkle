from nose.tools import assert_equal

from spikeylab.main.protocol_model import ProtocolTabelModel
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import PureTone
from PyQt4 import QtCore

class TestProtocolModel():
    def test_insert_emtpy_stim(self):
        model = ProtocolTabelModel()
        stim = StimulusModel()
        model.insertNewTest(stim,0)        

        assert_equal(stim, model.data(model.index(0,0), role=QtCore.Qt.UserRole))
        assert model.data(model.index(0,2), role=QtCore.Qt.DisplayRole) == 0

    def test_insert_remove_stim(self):
        model = ProtocolTabelModel()
        stim = StimulusModel()
        component = PureTone()
        stim.insertComponent(component, (0,0))
        model.insertNewTest(stim,0)        

        assert_equal(stim, model.data(model.index(0,0), role=QtCore.Qt.UserRole))
        assert_equal(stim, model.stimulusList()[0])
        assert model.data(model.index(0,1), role=QtCore.Qt.DisplayRole) == 1
        assert model.data(model.index(0,2), role=QtCore.Qt.DisplayRole) == 1
        assert model.data(model.index(0,3), role=QtCore.Qt.DisplayRole) == 1
        assert model.data(model.index(0,4), role=QtCore.Qt.DisplayRole) == stim.samplerate()
        assert model.rowCount() == 1

        model.removeTest(0)

        assert model.rowCount() == 0
        assert_equal([], model.stimulusList())

    def test_edit_model(self):

        model = ProtocolTabelModel()
        stim = StimulusModel()
        component = PureTone()
        stim.insertComponent(component, (0,0))
        model.insertNewTest(stim,0)

        assert stim.repCount() == 1

        newreps = 3
        model.setData(model.index(0,1), newreps, QtCore.Qt.EditRole)

        assert stim.repCount() == newreps
        assert model.data(model.index(0,1), role=QtCore.Qt.DisplayRole) == newreps
        assert model.data(model.index(0,2), role=QtCore.Qt.DisplayRole) == 1
        assert model.data(model.index(0,3), role=QtCore.Qt.DisplayRole) == newreps
