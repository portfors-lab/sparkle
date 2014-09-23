import cPickle

from nose.tools import assert_equal
from PyQt4 import QtCore, QtGui, QtTest

from spikeylab.run.protocol_model import ProtocolTabelModel
from spikeylab.gui.qprotocol import QProtocolTabelModel, ProtocolView
from spikeylab.stim.stimulus_model import StimulusModel
from spikeylab.gui.stim.factory import BuilderFactory
from spikeylab.gui.drag_label import DragLabel

import qtbot

ALLOW = 15

class TestProtocolView():
    def setUp(self):
        pass

    def test_drop_new_stim(self):
        view = ProtocolView()
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)
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
        view, stim = self.createView()

        view.model().removeTest(0)

        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-protocol", cPickle.dumps(stim))
        drop = QtGui.QDropEvent(QtCore.QPoint(), QtCore.Qt.MoveAction,
                                mimeData, QtCore.Qt.RightButton, 
                                QtCore.Qt.NoModifier)

        # hack to set the source without creating QDrag
        drop.source = lambda: view
        view.dropEvent(drop)

        assert view.model().rowCount() == 1
        assert_equal([stim], view.model().stimulusList())

    def test_draw_view(self):
        view, stim = self.createView()

        view.show()
        # this will still work even if no test... 
        assert view.grabImage(view.model().index(0,0)) is not None

    def test_set_user_tag(self):
        tag = 'sparkles'
        view, stim = self.createView()
        view.show()
        qtbot.click(view, view.model().index(0,0))
        QtTest.QTest.qWait(ALLOW)
        qtbot.type_msg(tag)
        QtTest.QTest.qWait(ALLOW)
        qtbot.keypress('enter')
        QtTest.QTest.qWait(ALLOW)

        assert view.model().data(view.model().index(0,0), QtCore.Qt.DisplayRole) == tag
        assert stim.userTag() == tag

        view.close()

    def createView(self):
        view = ProtocolView()
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)
        view.setModel(model)
        stim = StimulusModel()
        model.insertTest(stim, 0)
        return view, stim