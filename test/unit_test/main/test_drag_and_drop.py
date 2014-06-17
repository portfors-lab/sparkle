from spikeylab.main.control import MainWindow
from spikeylab.stim.factory import BuilderFactory, TCFactory
from spikeylab.stim.auto_parameter_view import AddLabel
from spikeylab.main.drag_label import DragLabel
from spikeylab.stim.types.stimuli_classes import PureTone
from spikeylab.data.dataobjects import AcquisitionData
from spikeylab.stim.abstract_parameters import AbstractParameterWidget
from test.util import robot, qttools

import sys 
import time, os, glob
import json
import threading

import h5py

from PyQt4 import QtGui, QtCore, QtTest


app = None
def setUp():
    global app
    app = QtGui.QApplication(sys.argv)

def tearDown():
    global app
    app.exit(0)

class TestDragNDrop():
    def setUp(self):
        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        fname = os.path.join(self.tempfolder, 'testdatafile.hdf5')
        self.form = MainWindow(datafile=fname, filemode='w')
        self.form.show()

    def tearDown(self):
        self.form.close()
        QtGui.QApplication.closeAllWindows()
        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

    def test_tone_protocol(self):
        self.form.ui.tab_group.setCurrentIndex(1)
        self.form.ui.reprate_spnbx.setValue(10)

        QtGui.QApplication.processEvents()
        pv = self.form.ui.protocolView
        
        label_pos = qttools.center(self.form.ui.stimulus_choices.builder_lbl)
        protocol_pos = qttools.center(pv)

        self.drag(label_pos, protocol_pos)

        assert self.form.acqmodel.protocol_model().rowCount() == 1

        item_pos = qttools.center(pv.visualRect(pv.model().index(0,1)), pv.viewport())
        robot.doubleclick(item_pos)
        QtTest.QTest.qWait(100)

        assert hasattr(pv, 'stim_editor')

        stim_editor = pv.stim_editor
        track_pos = qttools.center(stim_editor.ui.trackview)

        tone_label_pos = qttools.center(stim_editor.ui.template_box.getLabelByName('pure tone'))
        self.drag(tone_label_pos, track_pos)
        robot.keypress('enter')

        assert stim_editor.ui.trackview.model().componentCount() == 1
        # just use default tone settings, for now at least
        robot.click(qttools.center(stim_editor.ui.ok_btn))

        robot.click(qttools.center(self.form.ui.start_btn))
        QtTest.QTest.qWait(10)
        assert self.form.ui.running_label.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()

        while self.form.ui.running_label.text() == "RECORDING":
            QtTest.QTest.qWait(1000)

        assert self.form.ui.running_label.text() == "OFF"

    def drag(self, source, dest):
        dragthread = threading.Thread(target=robot.mousedrag, args=(source, dest))
        dragthread.start()
        while dragthread.is_alive():
            QtTest.QTest.qWait(1000)

    def close_modal(self):
        dialogs = []
        while len(dialogs) == 0:
            topWidgets = QtGui.QApplication.topLevelWidgets()
            dialogs = [w for w in topWidgets if isinstance(w, QtGui.QDialog)]
            time.sleep(1)
        robot.click(qttools.center(dialogs[0].ui.ok_btn))

