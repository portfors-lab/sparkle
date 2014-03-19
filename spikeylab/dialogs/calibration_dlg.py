from PyQt4 import QtGui, QtCore
from caldialog_form import Ui_CalibrationDialog
from spikeylab.data.dataobjects import load_calibration_file
from spikeylab.plotting.pyqtgraph_widgets import SimplePlotWidget

class CalibrationDialog(QtGui.QDialog):
    def __init__(self, fscale, default_vals=None):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_CalibrationDialog()
        self.ui.setupUi(self)
        # self.installEventFilter(self.eventFilter)
        if default_vals is not None:
            self.ui.calfile_lnedt.setText(default_vals['calfile'])
            self.ui.caldb_spnbx.setValue(default_vals['caldb'])
            self.ui.calv_spnbx.setValue(default_vals['calv'])
            self.ui.calf_spnbx.setValue(default_vals['calf']/fscale)
            self.ui.calfile_radio.setChecked(default_vals['use_calfile'])
            self.ui.frange_low_spnbx.setValue(default_vals['frange'][0]/fscale)
            self.ui.frange_high_spnbx.setValue(default_vals['frange'][1]/fscale)
        self.fscale = fscale
        self.pw = None

    def browseFiles(self):
        calfile = QtGui.QFileDialog.getOpenFileName(self, u"Select calibration file", 
                                    self.ui.calfile_lnedt.text(), "Calibration data files(*.hdf5 *.h5)")
        if calfile is not None:
            self.ui.calfile_lnedt.setText(calfile)

    def maxRange(self):
        try:
            x, freqs = load_calibration_file(self.ui.calfile_lnedt.text())
            self.ui.frange_low_spnbx.setValue(freqs[0]/self.fscale)
            self.ui.frange_high_spnbx.setValue(freqs[-1]/self.fscale)
        except IOError:
            QtGui.QMessageBox.warning(self, "File Read Error", "Unable to read calibration file")
        except KeyError:
            QtGui.QMessageBox.warning(self, "File Data Error", "Unable to find data in file")
           

    def plotCurve(self):
        try:
            attenuations, freqs = load_calibration_file(self.ui.calfile_lnedt.text())
            self.pw = SimplePlotWidget(freqs, attenuations, parent=self)
            self.pw.setWindowFlags(QtCore.Qt.Window)
            self.pw.set_labels('Frequency', 'Attenuation', 'Calibration Curve')
            self.pw.show()
        except IOError:
            QtGui.QMessageBox.warning(self, "File Read Error", "Unable to read calibration file")
        except KeyError:
            QtGui.QMessageBox.warning(self, "File Data Error", "Unable to find data in file")
           

    def values(self):
        results = {}
        results['use_calfile'] = self.ui.calfile_radio.isChecked()
        results['calfile'] = self.ui.calfile_lnedt.text()
        results['caldb'] = self.ui.caldb_spnbx.value()
        results['calv'] = self.ui.calv_spnbx.value()
        results['calf'] = self.ui.calf_spnbx.value()*self.fscale
        results['frange'] = (self.ui.frange_low_spnbx.value()*self.fscale, self.ui.frange_high_spnbx.value()*self.fscale)
        return results

    def conditional_accept(self):
        if self.ui.calfile_radio.isChecked() and self.ui.calfile_lnedt.text() == '':
            self.ui.none_radio.setChecked(True)
        if self.ui.calfile_radio.isChecked():
            try:
                x, freqs = load_calibration_file(self.ui.calfile_lnedt.text())
            except IOError:
                QtGui.QMessageBox.warning(self, "File Read Error", "Unable to read calibration file")
                return
            if self.ui.frange_low_spnbx.value()*self.fscale < freqs[0] or \
                self.ui.frange_high_spnbx.value()*self.fscale > freqs[-1]:
                QtGui.QMessageBox.warning(self, "Invalid Frequency Range", 
                    "Provided frequencys outside of calibration file range of {} - {} Hz".format(freqs[0], freqs[-1]))
                return

        self.accept()
