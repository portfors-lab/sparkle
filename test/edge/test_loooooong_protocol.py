import os
import json
import glob

from PyQt4 import QtGui, QtCore, QtTest
import h5py

from spikeylab.gui.control import MainWindow
from spikeylab.stim.stimulus_model import StimulusModel
from spikeylab.gui.stim.factory import TCFactory
from spikeylab.tools.systools import rand_id

import qtbot
import test.sample as sample

class TestMainUI():
    def setUp(self):
        
        self.app = QtGui.QApplication([])

        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        if not os.path.exists(self.tempfolder):
            os.mkdir(self.tempfolder)
        fname = os.path.join(self.tempfolder, 'testdatafile' +rand_id()+'.hdf5')
        self.fname = fname
        self.form = MainWindow(datafile=fname, filemode='w')
        self.form.ui.reprateSpnbx.setValue(10)
        self.form.ui.tabGroup.setCurrentIndex(1)
        self.form.show()
        # so that the data display doesn't get in the way of out
        # mouse movements
        self.form.ui.plotDock.close()
        self.form.showMaximized()
        QtGui.QApplication.processEvents()

    def tearDown(self):
        self.form.close()
        QtGui.QApplication.closeAllWindows()

        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)
        del self.app

    def test_long_protocol(self):

        winsz = 0.5
        self.form.ui.windowszSpnbx.setValue(winsz*1000)

        # test out a long running protocol, and to make sure nothing bad happens
        with open(sample.batlabvocal(), 'r') as jf:
            state = json.load(jf)
        stim0 = StimulusModel.loadFromTemplate(state)
        self.form.acqmodel.protocol_model().insert(stim0,0)

        tc0 = StimulusModel()
        TCFactory().init_stim(tc0)
        tc0.setRepCount(25)
        self.form.acqmodel.protocol_model().insert(tc0,0)

        with open(sample.reallylong(), 'r') as jf:
                    state = json.load(jf)
        stim1 = StimulusModel.loadFromTemplate(state)
        self.form.acqmodel.protocol_model().insert(stim1,0)

        tc1 = StimulusModel()
        TCFactory().init_stim(tc1)
        tc1.setRepCount(25)
        self.form.acqmodel.protocol_model().insert(tc1,0)
        QtGui.QApplication.processEvents()

        qtbot.click(self.form.ui.startBtn)

        QtTest.QTest.qWait(15)
        assert self.form.ui.runningLabel.text() == "RECORDING"

        # modal dialog will block qt methods in main thread
        qtbot.handle_modal_widget(wait=True)

        acqrate = self.form.ui.aisrSpnbx.value()*self.form.fscale
        self.form.close()

        hfile = h5py.File(self.fname)
        assert 'segment_1' in hfile.keys()
        assert 'test_1' in hfile['segment_1'].keys()
        assert hfile['segment_1']['test_1'].shape == (stim0.traceCount()+1, stim0.repCount(), winsz*acqrate)
        assert hfile['segment_1']['test_2'].shape == (tc0.traceCount()+1, tc0.repCount(), winsz*acqrate)
        assert hfile['segment_1']['test_3'].shape == (stim1.traceCount()+1, stim1.repCount(), winsz*acqrate)
        assert hfile['segment_1']['test_4'].shape == (tc1.traceCount()+1, tc1.repCount(), winsz*acqrate)