import glob
import os
import threading
import time

from nose.tools import assert_equal

import qtbot
from sparkle.QtWrapper import QtGui, QtTest
from sparkle.acq.daq_tasks import get_devices
from sparkle.gui.main_control import MainWindow


class TestMainDialogs():
    """Just trying to test the code which launches dialogs, and
    handles results, not the dialogs themselves"""
    def setUp(self):

        self.tempfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp")
        fname = os.path.join(self.tempfolder, 'testdatafile.hdf5')
        self.form = MainWindow(datafile=fname, filemode='w-')
        self.form.ui.plotDock.close()
        self.form.show()

    def tearDown(self):
        self.form.close()
        QtGui.QApplication.closeAllWindows()
        QtGui.QApplication.processEvents()

        # delete all data files in temp folder -- this will also clear out past
        # test runs that produced errors and did not delete their files
        files = glob.glob(self.tempfolder + os.sep + '[a-zA-Z0-9_]*.hdf5')
        for f in files:
            os.remove(f)

    def test_save_dlg(self):
        # modal dialog will block qt methods in main thread
        qtbot.handle_dialog()
        t = self.form.launchSaveDlg()
        t.join()
        assert self.form.ui.dataFileLbl.text() == os.path.basename(self.form.acqmodel.current_data_file())

    def test_calibration_dlg(self):
        qtbot.handle_dialog()
        self.form.launchCalibrationDlg()
        assert self.form.ui.currentCalLbl.text() == 'None'

    def test_scale_dlg(self):
        fscale = self.form.fscale
        tscale = self.form.tscale
        qtbot.handle_dialog()
        QtTest.QTest.qWait(100)
        self.form.launchScaleDlg()
        assert fscale == self.form.fscale
        assert tscale == self.form.tscale

    def test_specgram_dlg(self):
        sargs = self.form.specArgs.copy()
        qtbot.handle_dialog()
        self.form.launchSpecgramDlg()
        assert_equal(sargs, self.form.specArgs)

    def test_view_dlg(self):
        vsettings = self.form.viewSettings.copy()
        qtbot.handle_dialog()
        self.form.launchViewDlg()
        assert vsettings['fontsz'] == self.form.viewSettings['fontsz']

    def test_cell_id_dlg(self):
        cid = self.form.acqmodel.current_cellid
        qtbot.handle_dialog()
        self.form.launchCellDlg()
        assert cid == self.form.acqmodel.current_cellid

    def test_advanced_options_dlg(self):
        options = self.form.advanced_options.copy()
        device_name = get_devices()
        if len(device_name) > 0:
            options['device_name'] = device_name[0]
        qtbot.handle_dialog()
        self.form.launchAdvancedDlg()
        assert_equal(self.form.advanced_options, options)

    def test_channel_dlg(self):
        chans = self.form._aichans[:]
        deets = self.form._aichan_details.copy()
        qtbot.handle_dialog()
        self.form.launchChannelDlg()
        assert chans == self.form._aichans
        assert_equal(self.form._aichan_details, deets)
