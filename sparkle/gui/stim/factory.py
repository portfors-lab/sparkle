"""
Factory classes for intializing :class:`StimulusModels<sparkle.stim.stimulus_model.StimulusModel>`
and assigning editors to them
"""
import json
import os

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.stim.stimulus_editor import StimulusEditor
from sparkle.gui.stim.tuning_curve import TuningCurveEditor
from sparkle.stim import get_stimulus_editor
from sparkle.stim.auto_parameter_model import AutoParameterModel
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import PureTone


class StimFactory():
    """Abstract Class for all factories to re-implement"""
    name = 'unknown'
    def editor(self):
        """Returns an implemented AbstractStimulusWidget class appropriate
        for this stimulus

        :returns: (subclass of) :class:`AbstractStimulusWidget<sparkle.gui.stim.abstract_stim_editor.AbstractStimulusWidget>`      
        """
        raise NotImplementedError

    def create(self):
        """create a new stimulus model object

        :returns: :class:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel>`
        """
        raise NotImplementedError

class BuilderFactory(StimFactory):
    """Class with no further intialization and the most powerful editor"""
    name = 'Builder'
    def editor(self):
        return StimulusEditor

    def create(self):
        stim = StimulusModel()
        stim.setStimType(StimulusEditor.name)
        stim.setRepCount(StimulusEditor.defaultReps())
        return stim

class TCFactory(StimFactory):
    """Intializes stimulus to have a single tone with frequency
     and intensity autoparameters"""
    name = 'Tuning Curve' #name that shows up on drag label
    def editor(self):
        return TuningCurveEditor

    @staticmethod
    def create():
        stim = StimulusModel()

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
        return stim

class CCFactory(StimFactory):
    """Intializes stimulus to have a single tone with frequency
     and intensity autoparameters"""
    name = 'Calibration Curve'
    def editor(self):
        return TuningCurveEditor

    @staticmethod
    def create():
        stim = StimulusModel()
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
        return stim

class TemplateFactory(StimFactory):
    """Initializes stimulus to load values and editor type that
     were saved to file"""
    name = 'Saved'
    save_folder = os.path.expanduser('~')
    _editor = None
    def editor(self):
        return self._editor

    def create(self):
        stim = StimulusModel()
        # load saved settings into stimulus
        fname = QtGui.QFileDialog.getOpenFileName(None, u"Load Stimulus from File", 
                                    self.save_folder, "Stimulus Settings (*.json)")
        if fname:
            with open(fname, 'r') as jf:
                state = json.load(jf)
            stim.loadFromTemplate(state, stim)
            self._editor = get_stimulus_editor(stim.stimType())
        else:
            return None
        return stim
