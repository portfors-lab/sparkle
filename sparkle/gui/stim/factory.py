"""
Factory classes for intializing :class:`StimulusModels<sparkle.stim.stimulus_model.StimulusModel>`
and assigning editors to them
"""
import json
import os

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.stim.stimulus_editor import StimulusEditor
from sparkle.gui.stim.tuning_curve import TuningCurveEditor
from sparkle.stim.auto_parameter_model import AutoParameterModel
from sparkle.stim.stimulus_model import StimulusModel
from sparkle.stim.types.stimuli_classes import PureTone


class StimFactory():
    """Abstract Class for all factories to re-implement"""
    name = 'unknown'
    defaultInputs = {}
    def create(self):
        """create a new stimulus model object

        :returns: :class:`StimulusModel<sparkle.stim.stimulus_model.StimulusModel>`
        """
        raise NotImplementedError

    @staticmethod
    def update(defaults):
        pass

class BuilderFactory(StimFactory):
    """Class with no further intialization and the most powerful editor"""
    name = 'Builder'
    def create(self):
        stim = StimulusModel()
        stim.setStimType(BuilderFactory.name)
        stim.setRepCount(StimulusEditor.defaultReps())
        return stim

class TCFactory(StimFactory):
    """Intializes stimulus to have a single tone with frequency
     and intensity autoparameters"""
    name = 'Tuning Curve' #name that shows up on drag label
    defaultInputs = { 'duration':0.05, 'risefall':0.003, 'reps':1, 'freqStart':1000, 'freqStop':100000, 'freqStep':10000, 
        'intenStart':60, 'intenStop':70, 'intenStep':10 }
    @staticmethod
    def create():
        stim = StimulusModel()

        tone = PureTone()
        tone.setDuration(TCFactory.defaultInputs['duration'])
        tone.setRisefall(TCFactory.defaultInputs['risefall'])
        stim.insertComponent(tone)

        tuning_curve = stim.autoParams()

        tuning_curve.insertRow(0)
        tuning_curve.toggleSelection(0, tone)
        tuning_curve.setParamValue(0, parameter='frequency', start=TCFactory.defaultInputs['freqStart'], stop=TCFactory.defaultInputs['freqStop'], step=TCFactory.defaultInputs['freqStep'])
        tuning_curve.insertRow(1)
        tuning_curve.toggleSelection(1, tone)
        tuning_curve.setParamValue(1, parameter='intensity', start=TCFactory.defaultInputs['intenStart'], stop=TCFactory.defaultInputs['intenStop'], step=TCFactory.defaultInputs['intenStep'])

        stim.setRepCount(TCFactory.defaultInputs['reps'])
        
        stim.setStimType(TCFactory.name)
        return stim

    @staticmethod
    def update(defaults):
        TCFactory.defaultInputs.update(defaults)

class CCFactory(StimFactory):
    """Intializes stimulus to have a single tone with frequency
     and intensity autoparameters"""
    name = 'Calibration Curve'
    defaultInputs = { 'duration':0.05, 'risefall':0.003, 'reps':1, 'freqStart':1000, 'freqStop':100000, 'freqStep':20000, 
        'intenStart':90, 'intenStop':100, 'intenStep':10 }
    @staticmethod
    def create():
        stim = StimulusModel()
        tone = PureTone()
        tone.setDuration(CCFactory.defaultInputs['duration'])
        tone.setRisefall(CCFactory.defaultInputs['risefall'])
        stim.insertComponent(tone)

        tuning_curve = stim.autoParams()

        tuning_curve.insertRow(0)
        tuning_curve.toggleSelection(0, tone)
        tuning_curve.setParamValue(0, parameter='frequency', start=CCFactory.defaultInputs['freqStart'], stop=CCFactory.defaultInputs['freqStop'], step=CCFactory.defaultInputs['freqStep'])
        tuning_curve.insertRow(1)
        tuning_curve.toggleSelection(1, tone)
        tuning_curve.setParamValue(1, parameter='intensity', start=CCFactory.defaultInputs['intenStart'], stop=CCFactory.defaultInputs['intenStop'], step=CCFactory.defaultInputs['intenStep'])

        stim.setRepCount(CCFactory.defaultInputs['reps'])

        stim.setStimType(CCFactory.name)
        return stim

    @staticmethod
    def update(defaults):
        CCFactory.defaultInputs.update(defaults)

class TemplateFactory(StimFactory):
    """Initializes stimulus to load values and editor type that
     were saved to file"""
    name = 'Saved'
    save_folder = os.path.expanduser('~')
    _editor = None
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


def get_stimulus_editor(name):
    # abstract this more
    if name == BuilderFactory.name:
        return StimulusEditor
    elif name == TCFactory.name or name == CCFactory.name:
        return TuningCurveEditor
    else:
        return None

def get_stimulus_factory(name):
    if name == TCFactory.name:
        return TCFactory
    elif name == CCFactory.name:
        return CCFactory
    else:
        return StimFactory