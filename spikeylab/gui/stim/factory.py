"""
Factory classes for intializing :class:`StimulusModels<spikeylab.stim.stimulusmodel.StimulusModel>`
and assigning editors to them
"""
import os
import json

from PyQt4 import QtGui, QtCore

from spikeylab.gui.stim.stimulus_editor import StimulusEditor
from spikeylab.gui.stim.tceditor import TuningCurveEditor
from spikeylab.stim.types.stimuli_classes import PureTone
from spikeylab.stim.auto_parameter_model import AutoParameterModel
from spikeylab.stim import get_stimulus_editor

class StimFactory():
    """Abstract Class for all factories to re-implement"""
    name = 'unknown'
    def editor(self):
        """Returns an implemented AbstractStimulusWidget class appropriate
        for this stimulus

        :returns: class:`AbstractStimulusWidget<spikeylab.gui.stim.abstract_stim_editor.AbstractStimulusWidget>`
        (subclass of)
        """
        raise NotImplementedError

    def init_stim(self, stim):
        """Initializes *stim*

        :param stim: :class:`StimulusModel<spikeylab.stim.stimulusmodel.StimulusModel>`
        """
        raise NotImplementedError

class BuilderFactory(StimFactory):
    """Class with no further intialization and the most powerful editor"""
    name = 'Builder'
    def editor(self):
        return StimulusEditor

    def init_stim(self, stim):
        stim.setStimType(StimulusEditor.name)

class TCFactory(StimFactory):
    """Intializes stimulus to have a single tone with frequency
     and intensity autoparameters"""
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

        tuning_curve.insertRow(0)
        tuning_curve.toggleSelection(0, tone)
        tuning_curve.setParamValue(0, parameter='frequency', start=1000, stop=100000, step=10000)
        tuning_curve.insertRow(1)
        tuning_curve.toggleSelection(1, tone)
        tuning_curve.setParamValue(1, parameter='intensity', start=60, stop=70, step=10)
        
        stim.setStimType(TuningCurveEditor.name)

class CCFactory(StimFactory):
    """Intializes stimulus to have a single tone with frequency
     and intensity autoparameters"""
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

        tuning_curve.insertRow(0)
        tuning_curve.toggleSelection(0, tone)
        tuning_curve.setParamValue(0, parameter='frequency', start=1000, stop=100000, step=20000)
        tuning_curve.insertRow(1)
        tuning_curve.toggleSelection(1, tone)
        tuning_curve.setParamValue(1, parameter='intensity', start=90, stop=100, step=10)

        stim.setStimType(TuningCurveEditor.name)

class TemplateFactory(StimFactory):
    """Initializes stimulus to load values and editor type that
     were saved to file"""
    name = 'Saved'
    save_folder = os.path.expanduser('~')
    _editor = None
    def editor(self):
        return self._editor

    def init_stim(self, stim):
        # load saved settings into stimulus
        fname = QtGui.QFileDialog.getOpenFileName(None, u"Load Stimulus from File", 
                                    self.save_folder, "Stimulus Settings (*.json)")
        if fname:
            with open(fname, 'r') as jf:
                state = json.load(jf)
            stim.loadFromTemplate(state, stim)
            self._editor = get_stimulus_editor(stim.stimType())
        else:
            return 1