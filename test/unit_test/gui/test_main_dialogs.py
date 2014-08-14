import os, glob
import threading, time

from PyQt4 import QtGui
from nose.tools import assert_equal

from spikeylab.gui.control import MainWindow

from test.util import robot

class TestMainDialogs():
    """Just trying to test the code which launches dialogs, and
    handles results, not the dialogs themselves"""
    def setUp(self):
        self.app = QtGui.QApplication([])

        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        fname = os.path.join(self.tempfolder, 'testdatafile.hdf5')
        self.form = MainWindow(datafile=fname, filemode='w')
        self.form.ui.plotDock.close()
        self.form.show()

    def tearDown(self):
        self.form.close()
        QtGui.QApplication.closeAllWindows()
        del self.app

        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

    def test_save_dlg(self):
        # modal dialog will block qt methods in main thread
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()
        self.form.launchSaveDlg()
        assert self.form.ui.dataFileLbl.text() == os.path.basename(self.form.acqmodel.current_data_file())

    def test_calibration_dlg(self):
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()
        self.form.launchCalibrationDlg()
        assert self.form.ui.currentCalLbl.text() == 'None'

    def test_scale_dlg(self):
        fscale = self.form.fscale
        tscale = self.form.tscale
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()
        self.form.launchScaleDlg()
        assert fscale == self.form.fscale
        assert tscale == self.form.tscale

    def test_specgram_dlg(self):
        sargs = self.form.specArgs.copy()
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()
        self.form.launchSpecgramDlg()
        assert_equal(sargs, self.form.specArgs)

    def test_view_dlg(self):
        vsettings = self.form.viewSettings.copy()
        dialogthread = threading.Thread(target=self.close_modal)
        dialogthread.start()
        self.form.launchViewDlg()
        assert vsettings['fontsz'] == self.form.viewSettings['fontsz']

    def close_modal(self):
        dialogs = []
        while len(dialogs) == 0:
            topWidgets = QtGui.QApplication.topLevelWidgets()
            dialogs = [w for w in topWidgets if isinstance(w, QtGui.QDialog)]
            time.sleep(1)
        robot.keypress('enter')