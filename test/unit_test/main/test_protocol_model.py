import sys
import cPickle
from nose.tools import assert_equal

from spikeylab.main.protocol_model import ProtocolTabelModel, ProtocolView
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import PureTone
from spikeylab.stim.stimulus_editor import BuilderFactory
from spikeylab.main.drag_label import FactoryLabel
from PyQt4 import QtCore, QtGui, QtTest

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
        assert_equal([stim], model.stimulusList())
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

class TestProtocolView():
    def setUp(self):
        pass

    def test_drop_new_stim(self):
        view = ProtocolView()
        model = ProtocolTabelModel()
        view.setModel(model)
        builder_label = FactoryLabel(BuilderFactory)
        
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-protocol", cPickle.dumps(BuilderFactory()))
        # construct a fake drop event
        drop = QtGui.QDropEvent(QtCore.QPoint(), QtCore.Qt.MoveAction,
                                mimeData, QtCore.Qt.LeftButton, 
                                QtCore.Qt.NoModifier)
        view.dropEvent(drop)

        assert model.rowCount() == 1

    def test_drop_prev_stim(self):
        view = ProtocolView()
        model = ProtocolTabelModel()
        view.setModel(model)
        stim = StimulusModel()
        model.insertNewTest(stim, 0)

        model.removeTest(0)

        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-protocol", cPickle.dumps(stim.stimid))
        drop = QtGui.QDropEvent(QtCore.QPoint(), QtCore.Qt.MoveAction,
                                mimeData, QtCore.Qt.RightButton, 
                                QtCore.Qt.NoModifier)
        view.dropEvent(drop)

        assert model.rowCount() == 1
        assert_equal([stim], model.stimulusList())
