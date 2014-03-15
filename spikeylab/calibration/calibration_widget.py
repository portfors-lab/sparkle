from PyQt4 import QtGui

from spikeylab.stim.tceditor import TuningCurveEditor
from .calwidget_form import Ui_CalibrationWidget

class CalibrationWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CalibrationWidget,self).__init__(parent)
        self.ui = Ui_CalibrationWidget()
        self.ui.setupUi(self)
        self.ui.curve_widget.ui.ok_btn.hide()
        self.ui.curve_widget.ui.save_btn.hide()
        self.ui.curve_widget.ui.dur_spnbx.setEnabled(False)

    def setCurveModel(self, model):
        """sets the StimulusModel for this calibration curve"""
        self.stim_model = model
        self.ui.curve_widget.setStimulusModel(model)

    def set_duration(self, dur):
        self.ui.curve_widget.ui.dur_spnbx.setValue(dur)
