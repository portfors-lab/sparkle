from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.stim.abstract_stim_editor import AbstractStimulusWidget
from sparkle.gui.stim.tuning_curve_form import Ui_TuningCurveEditor

RED = QtGui.QPalette()
RED.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.red)
BLACK = QtGui.QPalette()
BLACK.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text,QtCore.Qt.black)

class TuningCurveEditor(AbstractStimulusWidget, Ui_TuningCurveEditor):
    """Editor Widget for tuning curve StimulusModel"""
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
        self.ok = self.ui.okBtn

        # set scaling to current for application
        self.ui.freqStartSpnbx.setScale(self._scales[1])
        self.ui.freqStopSpnbx.setScale(self._scales[1])
        self.ui.freqStepSpnbx.setScale(self._scales[1])
        self.ui.durSpnbx.setScale(self._scales[0])
        self.ui.risefallSpnbx.setScale(self._scales[0])

        self.tunit_fields.append(self.ui.durSpnbx)
        self.tunit_fields.append(self.ui.risefallSpnbx)
        self.funit_fields.append(self.ui.freqStartSpnbx)
        self.funit_fields.append(self.ui.freqStopSpnbx)
        self.funit_fields.append(self.ui.freqStepSpnbx)

    def setModel(self, model):
        """Sets the StimulusModel for this editor"""
        self.stimModel = model
        self.parameterModel = model.autoParams()
        tone = self.stimModel.data(self.stimModel.index(0,0), QtCore.Qt.UserRole+1)
        info = tone.auto_details()

        # set max/mins
        fmax = info['frequency']['max']
        self.ui.freqStartSpnbx.setMaximum(fmax)
        self.ui.freqStopSpnbx.setMaximum(fmax)
        self.ui.freqStepSpnbx.setMaximum(500000)
        dbmax = info['intensity']['max']
        self.ui.dbStartSpnbx.setMaximum(dbmax)
        self.ui.dbStopSpnbx.setMaximum(dbmax)
        self.ui.dbStepSpnbx.setMaximum(500000)
        self.ui.durSpnbx.setMaximum(info['duration']['max'])
        self.ui.risefallSpnbx.setMaximum(info['risefall']['max'])

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

        self.ui.durSpnbx.setValue(tone.duration())
        self.ui.nrepsSpnbx.setValue(self.stimModel.repCount())
        self.ui.risefallSpnbx.setValue(tone.risefall())
        self.tone = tone

    def submit(self):
        # hack to get mapper to update values
        self.fmapper.submit()
        self.dbmapper.submit()
        self.fmapper.toFirst()
        self.dbmapper.setCurrentIndex(1)

    def setStimDuration(self):
        """Sets the duration of the StimulusModel from values pulled from
        this widget"""
        duration = self.ui.durSpnbx.value()
        self.tone.setDuration(duration)
        # self.stimModel.data(self.stimModel.index(0,0), QtCore.Qt.UserRole).setDuration(duration)

    def setStimReps(self):
        """Sets the reps of the StimulusModel from values pulled from
        this widget"""
        reps = self.ui.nrepsSpnbx.value()
        self.stimModel.setRepCount(reps)

    def setStimRisefall(self):
        """Sets the Risefall of the StimulusModel's tone from values pulled from
        this widget"""
        rf = self.ui.risefallSpnbx.value()
        self.tone.setRisefall(rf)

    def model(self):
        """Gets this editor's StimulusModel"""
        return self.stimModel

    def updateTextColor(self, txt):
        w = self.sender()
        if int(txt) == 0:
            w.setPalette(RED)
        else:
            w.setPalette(BLACK)

    def durationInputWidget(self):
        """Gets the input widget that handles duration"""
        return self.ui.durSpnbx

if __name__ == "__main__":
    import sys
    from sparkle.stim.auto_parameter_model import AutoParameterModel
    from sparkle.stim.stimulus_model import StimulusModel
    from sparkle.stim.types.stimuli_classes import *
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
