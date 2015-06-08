import cPickle
import os
import shutil

from nose.tools import assert_equal

import qtbot
from sparkle.QtWrapper import QtCore, QtGui, QtTest
from sparkle.gui.drag_label import DragLabel
from sparkle.gui.qprotocol import ProtocolView, QProtocolTabelModel
from sparkle.gui.stim.factory import BuilderFactory, TCFactory, TemplateFactory
from sparkle.run.protocol_model import ProtocolTabelModel
from sparkle.stim.stimulus_model import StimulusModel

ALLOW = 15

tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")

class TestProtocolView():
    def setUp(self):
        if not os.path.exists(tempfolder):
            os.mkdir(tempfolder)

    def tearDown(self):
        shutil.rmtree(tempfolder, ignore_errors=True)

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
        view, stim = self.createView()
        view.show()
        QtTest.QTest.qWait(200)
        tag = self.add_tag(view)
        
        assert view.model().data(view.model().index(0,0), QtCore.Qt.DisplayRole) == tag
        assert stim.userTag() == tag

        view.close()

    def test_save_reload_test(self):
        view, stim = self.createView()
        view.show()
        QtTest.QTest.qWait(200)
        tag = self.add_tag(view)
        fname = os.path.join(tempfolder,'save_tmp.json')

        # bring up editor to save stimulus...
        qtbot.doubleclick(view, view.model().index(0,0))
        qtbot.handle_modal_widget(wait=False, func=msg_enter, args=(fname,))

        QtTest.QTest.qWait(ALLOW)
        view.stimEditor.saveStimulus()
        view.stimEditor.close()
        QtTest.QTest.qWait(ALLOW)

        assert os.path.isfile(fname)

        view.model().clearTests()
        QtTest.QTest.qWait(ALLOW)
        assert view.model().rowCount() == 0
        builder_label = DragLabel(TemplateFactory)
        
        mimeData = QtCore.QMimeData()
        mimeData.setData("application/x-protocol", cPickle.dumps(TemplateFactory()))
        # construct a fake drop event
        drop = QtGui.QDropEvent(QtCore.QPoint(), QtCore.Qt.MoveAction,
                                mimeData, QtCore.Qt.LeftButton, 
                                QtCore.Qt.NoModifier)
        qtbot.handle_modal_widget(wait=False, func=msg_enter, args=(fname,))
        view.dropEvent(drop)

        assert view.model().rowCount() == 1
        assert view.model().data(view.model().index(0,0), QtCore.Qt.DisplayRole) == tag

    def add_tag(self, view):
        tag = 'sparkles'
        qtbot.click(view, view.model().index(0,0))
        QtTest.QTest.qWait(ALLOW)
        qtbot.type_msg(tag)
        QtTest.QTest.qWait(ALLOW)
        qtbot.keypress('enter')
        QtTest.QTest.qWait(ALLOW)
        return tag

    def createView(self):
        view = ProtocolView()
        tests = ProtocolTabelModel()
        tests.setReferenceVoltage(100, 0.1)
        model = QProtocolTabelModel(tests)
        view.setModel(model)
        stim = TCFactory.create()
        StimulusModel.setMaxVoltage(5.0, 5.0)
        model.insertTest(stim, 0)
        return view, stim

def msg_enter(widget, msg):
    qtbot.type_msg(msg)
    qtbot.keypress('enter')
