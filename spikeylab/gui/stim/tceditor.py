from PyQt4 import QtGui, QtCore

from spikeylab.gui.stim.abstract_editor import AbstractEditorWidget
from spikeylab.gui.stim.tcform import Ui_TuningCurveEditor

RED = QtGui.QPalette()
RED.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.red)
BLACK = QtGui.QPalette()
BLACK.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text,QtCore.Qt.black)

class TuningCurveEditor(AbstractEditorWidget, Ui_TuningCurveEditor):
    name = 'Tuning Curve' # name that show up in protocol list
    def __init__(self, parent=None):
        super(TuningCurveEditor, self).__init__(parent)
        self.ui = Ui_TuningCurveEditor()
        self.ui.setupUi(self)
        # using two mappers set to different rows at same time
        self.fmapper = QtGui.QDataWidgetMapper(self)
        self.dbmapper = QtGui.QDataWidgetMapper(self)

        # can't get mapper to map color
        self.ui.freqNstepsLbl.textChanged.connect(self.updateTextColor)
        self.ui.dbNstepsLbl.textChanged.connect(self.updateTextColor)

    def setStimulusModel(self, model):
        self.stimModel = model
        self.parameterModel = model.autoParams()

        self.fmapper.setModel(self.parameterModel)
        self.dbmapper.setModel(self.parameterModel)
        self.fmapper.addMapping(self.ui.freqStartSpnbx, 1)
        self.fmapper.addMapping(self.ui.freqStopSpnbx, 2)
        self.fmapper.addMapping(self.ui.freqStepSpnbx, 3)
        self.fmapper.addMapping(self.ui.freqNstepsLbl, 4, 'text')
        self.dbmapper.addMapping(self.ui.dbStartSpnbx, 1)
        self.dbmapper.addMapping(self.ui.dbStopSpnbx, 2)
        self.dbmapper.addMapping(self.ui.dbStepSpnbx, 3)
        self.dbmapper.addMapping(self.ui.dbNstepsLbl, 4, 'text')
        self.fmapper.toFirst()
        self.dbmapper.setCurrentIndex(1)

        tone = self.stimModel.data(self.stimModel.index(0,0), QtCore.Qt.UserRole)
        info = tone.auto_details()
        self.ui.durSpnbx.setValue(tone.duration()/info['duration']['multiplier'])
        self.ui.nrepsSpnbx.setValue(self.stimModel.repCount())
        self.ui.risefallSpnbx.setValue(tone.risefall()/info['risefall']['multiplier'])
        self.tone = tone

    def submit(self):
        # hack to get mapper to update values
        self.fmapper.submit()
        self.dbmapper.submit()
        self.fmapper.toFirst()
        self.dbmapper.setCurrentIndex(1)

    def setStimDuration(self):
        duration = self.ui.durSpnbx.value()
        info = self.tone.auto_details()
        self.tone.setDuration(duration*info['duration']['multiplier'])
        # self.stimModel.data(self.stimModel.index(0,0), QtCore.Qt.UserRole).setDuration(duration)

    def setStimReps(self):
        reps = self.ui.nrepsSpnbx.value()
        self.stimModel.setRepCount(reps)

    def setStimRisefall(self):
        rf = self.ui.risefallSpnbx.value()
        info = self.tone.auto_details()
        self.tone.setRisefall(rf*info['risefall']['multiplier'])

    def model(self):
        return self.stimModel

    def updateTextColor(self, txt):
        w = self.sender()
        if int(txt) == 0:
            w.setPalette(RED)
        else:
            w.setPalette(BLACK)

    def durationInputWidget(self):
        return self.ui.durSpnbx

if __name__ == "__main__":
    import sys
    from spikeylab.stim.auto_parameter_model import AutoParameterModel
    from spikeylab.stim.stimulusmodel import StimulusModel
    from spikeylab.stim.types.stimuli_classes import *
    app = QtGui.QApplication(sys.argv)

    tone0 = PureTone()
    tone0.setDuration(0.02)
    stim = StimulusModel()
    stim.insertComponent(tone0)

    tuning_curve = stim.autoParams()
    tuning_curve.insertRows(0,2)

    selection_model = tuning_curve.data(tuning_curve.index(0,0), role=AutoParameterModel.SelectionModelRole)
    selection_model.select(stim.index(0,0))
    selection_model = tuning_curve.data(tuning_curve.index(1,0), role=AutoParameterModel.SelectionModelRole)
    selection_model.select(stim.index(0,0))

    tuning_curve.setData(tuning_curve.index(0,0), 'frequency', role=QtCore.Qt.EditRole)
    tuning_curve.setData(tuning_curve.index(0,1), 0, role=QtCore.Qt.EditRole)
    tuning_curve.setData(tuning_curve.index(0,2), 150, role=QtCore.Qt.EditRole)
    tuning_curve.setData(tuning_curve.index(0,3), 10, role=QtCore.Qt.EditRole)
    tuning_curve.setData(tuning_curve.index(1,0), 'intensity', role=QtCore.Qt.EditRole)
    tuning_curve.setData(tuning_curve.index(1,1), 0, role=QtCore.Qt.EditRole)
    tuning_curve.setData(tuning_curve.index(1,2), 100, role=QtCore.Qt.EditRole)
    tuning_curve.setData(tuning_curve.index(1,3), 5, role=QtCore.Qt.EditRole)

    stim.setEditor(TuningCurveEditor)    
    e = stim.showEditor()
    e.show()
    app.exec_()
