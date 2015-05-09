import re

from calibration_dlg_form import Ui_CalibrationDialog
from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.plotting.pyqtgraph_widgets import SimplePlotWidget


class CalibrationDialog(QtGui.QDialog):
    """Dialog to set current calibration, and the frequency range to apply it to"""
    def __init__(self, fscale, defaultVals=None, datafile=None):
        super(CalibrationDialog, self).__init__()
        self.ui = Ui_CalibrationDialog()
        self.ui.setupUi(self)
        
        self.ui.frangeLowSpnbx.setScale(fscale)
        self.ui.frangeHighSpnbx.setScale(fscale)

        if datafile is not None:
            cal_names = datafile.calibration_list()
            self.ui.calChoiceCmbbx.insertItems(0, cal_names)
        if defaultVals is not None:
            if defaultVals['calname'] != '':
                calidx = cal_names.index(defaultVals['calname'])
                self.ui.calChoiceCmbbx.setCurrentIndex(calidx)
            self.ui.calfileRadio.setChecked(defaultVals['use_calfile'])
            self.ui.frangeLowSpnbx.setValue(defaultVals['frange'][0])
            self.ui.frangeHighSpnbx.setValue(defaultVals['frange'][1])
        self.fscale = fscale
        self.pw = None
        self.datafile = datafile
        # default Vals can't be none, or I need a separate calf arg
        self.calf = defaultVals['calf']

    def maxRange(self):
        """Sets the maximum range for the currently selection calibration,
        determined from its range of values store on file
        """
        try:
            x, freqs = self.datafile.get_calibration(str(self.ui.calChoiceCmbbx.currentText()), self.calf)
            self.ui.frangeLowSpnbx.setValue(freqs[0])
            self.ui.frangeHighSpnbx.setValue(freqs[-1])
            print 'set freq range', freqs[0], freqs[-1], freqs[0], freqs[-1]
        except IOError:
            QtGui.QMessageBox.warning(self, "File Read Error", "Unable to read calibration file")
        except KeyError:
            QtGui.QMessageBox.warning(self, "File Data Error", "Unable to find data in file")
           
    def plotCurve(self):
        """Shows a calibration curve, in a separate window, of the currently selected calibration"""
        try:
            attenuations, freqs = self.datafile.get_calibration(str(self.ui.calChoiceCmbbx.currentText()), self.calf)
            self.pw = SimplePlotWidget(freqs, attenuations, parent=self)
            self.pw.setWindowFlags(QtCore.Qt.Window)
            self.pw.setLabels('Frequency', 'Attenuation', 'Calibration Curve')
            self.pw.show()
        except IOError:
            QtGui.QMessageBox.warning(self, "File Read Error", "Unable to read calibration file")
        except KeyError:
            QtGui.QMessageBox.warning(self, "File Data Error", "Unable to find data in file")

    def values(self):
        """Gets the values the user input to this dialog

        :returns: dict of inputs:
        |               *'use_calfile'*: bool, -- whether to apply calibration at all
        |               *'calname'*: str, -- the name of the calibration dataset to use
        |               *'frange'*: (int, int), -- (min, max) of the frequency range to apply calibration to
        """
        results = {}
        results['use_calfile'] = self.ui.calfileRadio.isChecked()
        results['calname'] = str(self.ui.calChoiceCmbbx.currentText())
        results['frange'] = (self.ui.frangeLowSpnbx.value(), self.ui.frangeHighSpnbx.value())
        return results

    def conditional_accept(self):
        """Accepts the inputs if all values are valid and congruent.
        i.e. Valid datafile and frequency range within the given calibration dataset."""
        if self.ui.calfileRadio.isChecked() and str(self.ui.calChoiceCmbbx.currentText()) == '':
            self.ui.noneRadio.setChecked(True)
        if self.ui.calfileRadio.isChecked():
            try:
                x, freqs = self.datafile.get_calibration(str(self.ui.calChoiceCmbbx.currentText()), self.calf)
            except IOError:
                QtGui.QMessageBox.warning(self, "File Read Error", "Unable to read calibration file")
                return
            except KeyError:
                QtGui.QMessageBox.warning(self, "File Data Error", "Unable to find data in file")
                return
            if self.ui.frangeLowSpnbx.value()    < freqs[0] or \
                self.ui.frangeHighSpnbx.value() > freqs[-1]:
                QtGui.QMessageBox.warning(self, "Invalid Frequency Range", 
                    "Provided frequencys outside of calibration file range of {} - {} Hz".format(freqs[0], freqs[-1]))
                return

        self.accept()
