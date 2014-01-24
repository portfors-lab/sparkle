import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_editor import AbstractEditorWidget
from spikeylab.stim.tcform import Ui_TuningCurveEditor
from spikeylab.stim.types.stimuli_classes import PureTone
from spikeylab.stim.auto_parameter_model import AutoParameterModel

class TCFactory():
    name = 'Tuning Curve' #name that shows up on drag label
    def editor(self):
        return TuningCurveEditor

    def init_stim(self, stim):
        """
        takes and inital empty stim and populates 
        it with a default tuning curve
        """
        tone = PureTone()
        tone.setDuration(0.1)
        stim.insertComponent(tone)

        tuning_curve = stim.autoParams()
        tuning_curve.insertRows(0,2)

        selection_model = tuning_curve.data(tuning_curve.index(0,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim.index(0,0))
        selection_model = tuning_curve.data(tuning_curve.index(1,0), role=AutoParameterModel.SelectionModelRole)
        selection_model.select(stim.index(0,0))

        tuning_curve.setData(tuning_curve.index(0,0), 'frequency', role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(0,1), 0, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(0,2), 100, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(0,3), 10, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,0), 'intensity', role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,1), 20, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,2), 100, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,3), 10, role=QtCore.Qt.EditRole)

class TuningCurveEditor(AbstractEditorWidget, Ui_TuningCurveEditor):
    name = 'Tuning Curve' # name that show up in protocol list
    def __init__(self, parent=None):
        super(TuningCurveEditor, self).__init__(parent)
        self.ui = Ui_TuningCurveEditor()
        self.ui.setupUi(self)
        #hack using two mappers set to different rows
        self.fmapper = QtGui.QDataWidgetMapper(self)
        self.dbmapper = QtGui.QDataWidgetMapper(self)

    def setStimulusModel(self, model):
        self.stim_model = model
        self.parameter_model = model.autoParams()

        self.fmapper.setModel(self.parameter_model)
        self.dbmapper.setModel(self.parameter_model)
        self.fmapper.addMapping(self.ui.freq_start_spnbx, 1)
        self.fmapper.addMapping(self.ui.freq_stop_spnbx, 2)
        self.fmapper.addMapping(self.ui.freq_step_spnbx, 3)
        self.fmapper.addMapping(self.ui.freq_nsteps_lbl, 4, 'text')
        self.dbmapper.addMapping(self.ui.db_start_spnbx, 1)
        self.dbmapper.addMapping(self.ui.db_stop_spnbx, 2)
        self.dbmapper.addMapping(self.ui.db_step_spnbx, 3)
        self.dbmapper.addMapping(self.ui.db_nsteps_lbl, 4, 'text')
        self.fmapper.toFirst()
        self.dbmapper.setCurrentIndex(1)

        tone = self.stim_model.data(self.stim_model.index(0,0), QtCore.Qt.UserRole)
        info = tone.auto_details()
        self.ui.dur_spnbx.setValue(tone.duration()/info['duration']['multiplier'])
        self.ui.nreps_spnbx.setValue(self.stim_model.repCount())
        self.ui.risefall_spnbx.setValue(tone.risefall()/info['risefall']['multiplier'])
        self.tone = tone

    def submit(self):
        # hack to get mapper to update values
        self.fmapper.submit()
        self.dbmapper.submit()
        self.fmapper.toFirst()
        self.dbmapper.setCurrentIndex(1)

    def setStimDuration(self):
        duration = self.ui.dur_spnbx.value()
        info = self.tone.auto_details()
        self.tone.setDuration(duration*info['duration']['multiplier'])
        # self.stim_model.data(self.stim_model.index(0,0), QtCore.Qt.UserRole).setDuration(duration)

    def setStimReps(self):
        reps = self.ui.nreps_spnbx.value()
        self.stim_model.setRepCount(reps)

    def setStimRisefall(self):
        rf = self.ui.risefall_spnbx.value()
        info = self.tone.auto_details()
        self.tone.setRisefall(rf*info['risefall']['multiplier'])


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
