from spikeylab.dialogs import SavingDialog, ScaleDialog, SpecDialog, CalibrationDialog
from spikeylab.data.dataobjects import load_calibration_file

import test.sample as sample

from nose.tools import assert_equal

from PyQt4.QtTest import QTest 
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import Qt

app = None
def setUp():
    global app
    app = QApplication([])

def tearDown():
    global app
    app.exit(0)


class TestCalibrationDialog():
    def setUp(self):
        self.fscale = 1000
        self.defaults = {'calf':20000, 'caldb':100,  'calv':0.1, 'calfile':'', 
                         'use_calfile':False, 'frange':(5000, 1e5)}
        self.dlg = CalibrationDialog(fscale=self.fscale, default_vals=self.defaults)
        self.dlg.show()

    def test_no_calfile_accept(self):
        assert self.dlg.ui.none_radio.isChecked() == True
        QTest.mouseClick(self.dlg.ui.buttonBox.button(self.dlg.ui.buttonBox.Ok), Qt.LeftButton)
        return_vals = self.dlg.values()

        assert_equal(self.defaults, return_vals)

    def test_calfile_accept(self):
        self.dlg.ui.calfile_lnedt.setText(sample.calibration_filename())
        self.dlg.ui.calfile_radio.setChecked(True)
        assert self.dlg.ui.none_radio.isChecked() == False
        QTest.mouseClick(self.dlg.ui.buttonBox.button(self.dlg.ui.buttonBox.Ok), Qt.LeftButton)
        
        return_vals = self.dlg.values()
        assert return_vals['calfile'] == sample.calibration_filename()
        assert return_vals['use_calfile'] == True

    def test_frequency_range(self):
        self.dlg.ui.calfile_lnedt.setText(sample.calibration_filename())
        self.dlg.ui.calfile_radio.setChecked(True)

        QTest.mouseClick(self.dlg.ui.range_btn, Qt.LeftButton)
        x, freqs = load_calibration_file(sample.calibration_filename())
        assert self.dlg.ui.frange_low_spnbx.value()*self.fscale == freqs[0]
        assert self.dlg.ui.frange_high_spnbx.value()*self.fscale == freqs[-1]

    def test_plot_curve(self):
        self.dlg.ui.calfile_lnedt.setText(sample.calibration_filename())
        self.dlg.ui.calfile_radio.setChecked(True)

        QTest.mouseClick(self.dlg.ui.plot_btn, Qt.LeftButton)

        assert self.dlg.pw is not None

        self.dlg.pw.close()