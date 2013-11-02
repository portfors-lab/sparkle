from audiolab.tools.langtools import enum

class StimulusModel():
"""Model to represent a unique stimulus, holds all relevant parameters"""
    def __init__(self):
        ntracks = 0
        nreps = 0
        # 2D array of simulus components track number x component number
        segments = [[]]
        auto_params = []

    def print_stimulus(self):
        """This is for purposes of documenting what was presented"""

class TrackModel(QtCore.QAbstractListModel):

    def __init__(self, segments=[], parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self._segments = segments

    def data(self, index, role):

class AbstractStimulusComponent()
"""Represents a single component of a complete summed stimulus"""
    start_time = None
    duration = None
    fs = None
    intensity = None
    risefall = None
    # def __init__(self):

class AutoParameter():
    """Hold information for parameter modification loop"""
    components = []
    parameter = ""
    delta = None
    stop_type = 0 # 0 : stop time, 1 : N times
    stop_value = None

class Tone(StimulusComponent):
    pass

class PureTone(Tone):
    name = "puretone"
    frequency = None

class FMSweep(Tone):
    name = "fmsweep"
    start_frequency = None
    stop_frequency = None

class Vocalization(StimulusComponent):
    name = "vocalization"
    filename = None

class Noise(StimulusComponent):
    name = "noise"

class Silence(StimulusComponent):
    name = "silence"

class Modulation(StimulusComponent):
    modulation_frequency = None

class SAM(Modulation):
"""Sinusodal Amplitude Modulation"""
    name = "sam"

class SquareWaveModulation(Modulation):
    name = "squaremod"

class SFM(StimulusComponent):
    name = "sfm"

class Ripples(StimulusComponent):
    name = "ripples"