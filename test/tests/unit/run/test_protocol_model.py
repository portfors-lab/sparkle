from nose.tools import assert_equal

from sparkle.QtWrapper import QtCore
from sparkle.gui.qprotocol import QProtocolTabelModel
from sparkle.run.protocol_model import ProtocolTabelModel
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import PureTone


class TestQProtocolModel():
    def test_insert_emtpy_stim(self):
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)
        stim = StimulusModel()
        model.insertTest(stim,0)        

        assert_equal(stim, model.data(model.index(0,0), role=QtCore.Qt.UserRole+1))
        assert model.data(model.index(0,3), role=QtCore.Qt.DisplayRole) == 0

    def test_insert_remove_stim(self):
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)
        stim = StimulusModel()
        component = PureTone()
        stim.insertComponent(component, 0,0)
        model.insertTest(stim,0)        

        headers = model.allHeaders()
        repidx = headers.index('Reps')
        lenidx = headers.index('Length')
        totalidx = headers.index('Total')
        fsidx = headers.index('Generation rate')

        assert_equal(stim, model.data(model.index(0,0), role=QtCore.Qt.UserRole+1))
        assert_equal([stim], model.stimulusList())
        assert model.data(model.index(0,repidx), role=QtCore.Qt.DisplayRole) == 1
        assert model.data(model.index(0,lenidx), role=QtCore.Qt.DisplayRole) == 1
        assert model.data(model.index(0,totalidx), role=QtCore.Qt.DisplayRole) == 1
        assert model.data(model.index(0,fsidx), role=QtCore.Qt.DisplayRole) == stim.samplerate()
        assert model.rowCount() == 1

        model.removeTest(0)

        assert model.rowCount() == 0
        assert_equal([], model.stimulusList())

    def test_edit_model(self):
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)
        stim = StimulusModel()
        component = PureTone()
        stim.insertComponent(component, 0,0)
        model.insertTest(stim,0)

        assert stim.repCount() == 1

        newreps = 3
        headers = model.allHeaders()
        repidx = headers.index('Reps')
        lenidx = headers.index('Length')
        totalidx = headers.index('Total')
        model.setData(model.index(0,repidx), newreps, QtCore.Qt.EditRole)

        assert stim.repCount() == newreps
        assert model.data(model.index(0,repidx), role=QtCore.Qt.DisplayRole) == newreps
        assert model.data(model.index(0,lenidx), role=QtCore.Qt.DisplayRole) == 1
        assert model.data(model.index(0,totalidx), role=QtCore.Qt.DisplayRole) == newreps

    def test_verify_no_tests(self):
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)

        assert model.verify()

    def test_verify_no_refv(self):
        model = QProtocolTabelModel()
        stim = StimulusModel()
        model.insertTest(stim,0)

        assert model.verify()

    def test_verify_stim_fail(self):
        """
        Verification from stimulus comes back invalid
        """
        # emtpy stim in this case
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)
        stim = StimulusModel()
        model.insertTest(stim,0)

        assert model.verify()

    def test_verify_success(self):
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)
        stim = StimulusModel()
        component = PureTone()
        stim.insertComponent(component, 0,0)
        model.insertTest(stim,0)

        assert model.verify() == 0
