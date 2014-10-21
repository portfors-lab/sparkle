import os

from QtWrapper import QtGui, QtCore, QtTest

from spikeylab.stim.types.stimuli_classes import PureTone, Vocalization
from spikeylab.gui.stim.components.vocal_parameters import VocalParameterWidget
from spikeylab.stim.types import get_stimuli_models

from test import sample
import qtbot

class TestVocalizationEditor():
    def setUp(self):
        self.component = Vocalization()
        self.editor = VocalParameterWidget()
        self.editor.setComponent(self.component)

        fpath = sample.samplewav()
        parentdir, fname = os.path.split(fpath)
        self.editor.setRootDirs(parentdir, parentdir)
        self.editor.show()

    def xtest_file_order(self):
        # select all the (wav) files in folder
        # self.editor.filelistView.selectAll()
        QtGui.QApplication.processEvents()
        QtTest.QTest.qWait(2000)
        # qtbot.drag_view(self.editor.filelistView, (0,0), (2,0))
        # QtTest.QTest.qWait(100)

        original_order = self.editor.fileorder

        qtbot.handle_modal_widget(wait=False, func=reorder)
        qtbot.click(self.editor.orderBtn)
        QtTest.QTest.qWait(1000)

        new_order = self.editor.fileorder

        assert new_order == original_order

def reorder(widget):
    qtbot.drag_view(widget.orderlist, (0,0), (1,0))
    QtTest.QTest.qWait(1000)
    qtbot.click(widget.okBtn)