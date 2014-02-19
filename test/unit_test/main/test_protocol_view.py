from nose.tools import assert_equal

import cPickle

from spikeylab.main.protocol_model import ProtocolTabelModel, ProtocolView
from spikeylab.stim.stimulusmodel import StimulusModel

from spikeylab.stim.factory import BuilderFactory
from spikeylab.main.drag_label import DragLabel

from PyQt4 import QtCore, QtGui, QtTest

app = None
def setUp():
    global app
    app = QtGui.QApplication([])

def tearDown():
    global app
    app.exit(0)

class TestProtocolView():
    def setUp(self):
        pass

    def test_drop_new_stim(self):
        view = ProtocolView()
        model = ProtocolTabelModel()
        model.setReferenceVoltage(100, 0.1)
        view.setModel(model)
        builder_label = DragLabel(BuilderFactory)
        
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
        model.setReferenceVoltage(100, 0.1)
        view.setModel(model)
        stim = StimulusModel()
        model.insertNewTest(stim, 0)

        model.removeTest(0)

        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-protocol", cPickle.dumps(stim.stimid))
        drop = QtGui.QDropEvent(QtCore.QPoint(), QtCore.Qt.MoveAction,
                                mimeData, QtCore.Qt.RightButton, 
                                QtCore.Qt.NoModifier)

        # hack to set the source without creating QDrag
        drop.source = lambda: view
        view.dropEvent(drop)

        assert model.rowCount() == 1
        assert_equal([stim], model.stimulusList())

    def test_draw_view(self):
        view = ProtocolView()
        model = ProtocolTabelModel()
        model.setReferenceVoltage(100, 0.1)
        view.setModel(model)
        stim = StimulusModel()
        model.insertNewTest(stim, 0)

        view.show()
        # this will still work even if no test... 
        assert view.grabImage(model.index(0,0)) is not None

        