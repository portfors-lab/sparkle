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

    def test_insert_stim(self):
        model = ProtocolTabelModel()
        stim = StimulusModel()
        component = PureTone()
        stim.insertComponent(component, (0,0))
        model.insertNewTest(stim,0)        

        assert_equal(stim, model.data(model.index(0,0), role=QtCore.Qt.UserRole))
        assert_equal(stim, model.stimulusList()[0])
        assert model.data(model.index(0,2), role=QtCore.Qt.DisplayRole) == 1
