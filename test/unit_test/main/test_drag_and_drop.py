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

PAUSE = 200

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

    def xtest_tone_protocol(self):
        self.protocol_run({'pure tone':{'duration': 66, 'frequency': 22}, 'silence':{'duration': 33}})

    def test_auto_parameter_protocol(self):
        self.protocol_run({'pure tone':{'duration': 66, 'frequency': 22}, 'silence':{'duration': 33}},
            [['duration', 10, 50, 10]])

    def protocol_run(self, components, autoparams={}):
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
        QtTest.QTest.qWait(PAUSE)

        assert hasattr(pv, 'stim_editor')

        stim_editor = pv.stim_editor
        track_pos = qttools.center(stim_editor.ui.trackview)
        for name, vals in components.items():
            tone_label_pos = qttools.center(stim_editor.ui.template_box.getLabelByName(name))
            self.drag(tone_label_pos, track_pos)
            self.set_paramters(name, vals)
            robot.keypress('enter')

        assert stim_editor.ui.trackview.model().componentCount() == len(components)

        if len(components) == 2:
            # line one up behind the other.. could make more robust my investigating row and column count
            pos0 = qttools.center(stim_editor.ui.trackview.visualRect(stim_editor.ui.trackview.model().index(0,0)),stim_editor.ui.trackview.viewport())
            comp0len = stim_editor.ui.trackview.visualRect(stim_editor.ui.trackview.model().index(0,0)).width()
            pos0 = (pos0[0]+(comp0len/2)+15, pos0[1])
            pos1 = qttools.center(stim_editor.ui.trackview.visualRect(stim_editor.ui.trackview.model().index(1,0)),stim_editor.ui.trackview.viewport())
            self.drag(pos1,pos0)
            assert stim_editor.ui.trackview.model().duration() == sum([x['duration'] for x in components.values()])/1000.


        robot.click(qttools.center(stim_editor.ui.parametizer.hide_btn))
        QtGui.QApplication.processEvents()
        pztr = stim_editor.ui.parametizer.parametizer

        for i, param in enumerate(autoparams):
            add_pos = qttools.center(pztr.add_lbl)
            list_pos = qttools.center(pztr.param_list)
            print 'drag poses', add_pos, list_pos
            self.drag(add_pos, list_pos)
            # just select first component
            QtTest.QTest.qWait(PAUSE)
            robot.click(qttools.center(stim_editor.ui.trackview.visualRect(stim_editor.ui.trackview.model().index(0,0)),stim_editor.ui.trackview.viewport()))
            # fill in auto  parameter
            for j, param_item in enumerate(param):
                # click the field
                robot.click(qttools.center(pztr.param_list.visualRect(pztr.param_list.model().index(i,j)), pztr.param_list.viewport()))
                robot.type(str(param_item))
                QtTest.QTest.qWait(PAUSE)

        QtGui.QApplication.processEvents()
        QtTest.QTest.qWait(PAUSE)
        # just use default tone settings, for now at least
        robot.click(qttools.center(stim_editor.ui.ok_btn))

        # set the window size to stim len + 100ms
        robot.doubleclick(qttools.center(self.form.ui.windowsz_spnbx))
        robot.type(str(self.form.acqmodel.protocol_model().data(self.form.acqmodel.protocol_model().index(0,0),QtCore.Qt.UserRole).duration()*1000+100))

        robot.click(qttools.center(self.form.ui.start_btn))
        QtTest.QTest.qWait(10)
        assert self.form.ui.running_label.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()

        while self.form.ui.running_label.text() == "RECORDING":
            QtTest.QTest.qWait(500)

        assert self.form.ui.running_label.text() == "OFF"

    def drag(self, source, dest):
        dragthread = threading.Thread(target=robot.mousedrag, args=(source, dest))
        dragthread.start()
        while dragthread.is_alive():
            QtTest.QTest.qWait(500)

    def close_modal(self):
        dialogs = []
        while len(dialogs) == 0:
            topWidgets = QtGui.QApplication.topLevelWidgets()
            dialogs = [w for w in topWidgets if isinstance(w, QtGui.QDialog)]
            time.sleep(1)
        robot.click(qttools.center(dialogs[0].ui.ok_btn))

    def set_paramters(self, name, vals):
        # find an editor and set the parameters
        topWidgets = QtGui.QApplication.topLevelWidgets()
        editors = [w for w in topWidgets if isinstance(w, AbstractParameterWidget)]
        assert len(editors) == 1
        editor = editors[0]
        print 'editor fields', editor.input_widgets
        for field, val in vals.items():
            input_pos = qttools.center(editor.input_widgets[field])
            robot.doubleclick(input_pos)
            robot.type(str(val))
            QtTest.QTest.qWait(PAUSE)
