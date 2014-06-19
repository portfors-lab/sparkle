import logging

from PyQt4 import QtGui

from spikeylab.stim.types.stimuli_classes import WhiteNoise, FMSweep
from spikeylab.stim.tceditor import TuningCurveEditor
from .calwidget_form import Ui_CalibrationWidget

class CalibrationWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CalibrationWidget,self).__init__(parent)
        self.ui = Ui_CalibrationWidget()
        self.ui.setupUi(self)
        self.ui.curveWidget.ui.okBtn.hide()
        self.ui.curveWidget.ui.saveBtn.hide()
        self.ui.curveWidget.ui.durSpnbx.setEnabled(False)
        self.ui.curveWidget.ui.nrepsSpnbx.hide()
        self.ui.curveWidget.ui.label_31.hide()
        self.durationWidgets = [self.ui.curveWidget.ui.durSpnbx]

    def setCurveModel(self, model):
        """sets the StimulusModel for this calibration curve"""
        self.stimModel = model
        self.ui.curveWidget.setStimulusModel(model)

    def setDuration(self, dur):
        for w in self.durationWidgets:
            w.setValue(dur)

    def addOption(self, stim):
        # set the editor widgets for noise and sweep
        self.ui.calTypeCmbbx.insertItem(0,stim.name)
        editor = stim.showEditor()
        # should probably make this less coupled
        durInput = editor.durationInputWidget()
        self.durationWidgets.append(durInput)
        durInput.setEnabled(False)
        self.ui.caleditorStack.insertWidget(0, editor)
        self.ui.calTypeCmbbx.setCurrentIndex(0)

    def saveToObject(self):
        for i in range(self.ui.caleditorStack.count()):
            try:
                self.ui.caleditorStack.widget(i).saveToObject()
            except AttributeError:
                logger = logging.getLogger('main')
                logger.debug('index {} does not have method saveToObject'.format(i))

    def currentIndex(self):
        return self.ui.calTypeCmbbx.currentIndex()

    def currentSelection(self):
        return self.ui.calTypeCmbbx.currentText()
        
    def isToneCal(self):
        return self.ui.calTypeCmbbx.currentIndex() == self.ui.calTypeCmbbx.count() -1

    def saveChecked(self):
        return self.ui.savecalCkbx.isChecked()