import os
import json

from PyQt4 import QtGui, QtCore

from spikeylab.stim.stimulus_editor import StimulusEditor
from spikeylab.stim.tceditor import TuningCurveEditor
from spikeylab.stim.types.stimuli_classes import PureTone
from spikeylab.stim.auto_parameter_model import AutoParameterModel

class StimFactory():
    name = 'unknown'
    def editor(self):
        raise NotImplementedError

    def init_stim(self, stim):
        raise NotImplementedError

class BuilderFactory(StimFactory):
    name = 'Builder'
    def editor(self):
        return StimulusEditor

    def init_stim(self, stim):
        pass

class TCFactory(StimFactory):
    name = 'Tuning Curve' #name that shows up on drag label
    def editor(self):
        return TuningCurveEditor

    @staticmethod
    def init_stim(stim):
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
        tuning_curve.setData(tuning_curve.index(0,1), 1, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(0,2), 100, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(0,3), 10, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,0), 'intensity', role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,1), 10, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,2), 100, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,3), 10, role=QtCore.Qt.EditRole)

class CCFactory(StimFactory):
    name = 'Calibration Curve'
    def editor(self):
        return TuningCurveEditor

    @staticmethod
    def init_stim(stim):
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
        tuning_curve.setData(tuning_curve.index(0,2), 200, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(0,3), 10, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,0), 'intensity', role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,1), 90, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,2), 100, role=QtCore.Qt.EditRole)
        tuning_curve.setData(tuning_curve.index(1,3), 10, role=QtCore.Qt.EditRole)

class TemplateFactory(StimFactory):
    name = 'Saved'
    save_folder = os.path.expanduser('~')
    _editor = None
    def editor(self):
        return self._editor

    def init_stim(self, stim):
        # load saved settings into stimulus
        fname = QtGui.QFileDialog.getOpenFileName(None, u"Load Stimulus from File", 
                                    self.save_folder, "Stimulus Settings (*.json)")
        with open(fname, 'r') as jf:
            state = json.load(jf)
        stim.loadFromTemplate(state, stim)
        self._editor = stim.editor