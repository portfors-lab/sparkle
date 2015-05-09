from sparkle.QtWrapper import QtGui
from scale_dlg_form import Ui_ScaleDlg
from sparkle.gui.stim.smart_spinbox import SmartSpinBox


class ScaleDialog(QtGui.QDialog):
    """Dialog for setting the time and frequency scaling for the GUI"""
    def __init__(self,  parent=None, defaultVals=None):
        super(ScaleDialog, self).__init__(parent)
        self.ui = Ui_ScaleDlg()
        self.ui.setupUi(self)

        if defaultVals is not None:
            if defaultVals[u'fscale'] == SmartSpinBox.Hz:
                self.ui.hzBtn.setChecked(True)
            elif defaultVals[u'fscale'] == SmartSpinBox.kHz:
                self.ui.khzBtn.setChecked(True)
            else:
                raise Exception(u"Invalid frequency scale")

            if defaultVals[u'tscale'] == SmartSpinBox.Seconds:
                self.ui.secBtn.setChecked(True)
            elif defaultVals[u'tscale'] == SmartSpinBox.MilliSeconds:
                self.ui.msBtn.setChecked(True)
            else:
                raise Exception(u"Invalid time scale")

    def values(self):
        """Gets the scales that the user chose

        | For frequency: 1 = Hz, 1000 = kHz
        | For time: 1 = seconds, 0.001 = ms

        :returns: float, float -- frequency scaling, time scaling
        """
        if self.ui.hzBtn.isChecked():
            fscale = SmartSpinBox.Hz
        else:
            fscale = SmartSpinBox.kHz

        if self.ui.msBtn.isChecked():
            tscale = SmartSpinBox.MilliSeconds
        else:
            tscale = SmartSpinBox.Seconds

        return fscale, tscale
