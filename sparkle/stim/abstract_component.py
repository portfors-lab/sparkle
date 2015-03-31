import cPickle
import uuid


class AbstractStimulusComponent(object):
    """Represents a single component of a complete summed stimulus"""
    name = 'unknown'
    protocol = False
    explore = False
    _start_time = None
    _duration = .01 # in seconds
    _intensity = 20 # in dB SPL
    _risefall = 0.003
    def __init__(self):
        self.idnum = uuid.uuid1()

    def duration(self):
        return self._duration

    def setDuration(self, dur):
        self._duration = dur

    def intensity(self):
        return self._intensity

    def setIntensity(self, intensity):
        self._intensity = intensity
        
    def risefall(self):
        return self._risefall

    def setRisefall(self, risefall):
        self._risefall = risefall    

    def set(self, param, value):
        setattr(self, '_'+param, value)

    def amplitude(self, caldb, calv, atten=0):
        """Calculates the voltage amplitude for this stimulus, using
        internal intensity value and the given reference intensity & voltage

        :param caldb: calibration intensity in dbSPL
        :type caldb: float
        :param calv: calibration voltage that was used to record the intensity provided
        :type calv: float
        """
        amp = (10 ** (float(self._intensity+atten-caldb)/20)*calv)
        return amp

    def signal(self, fs, atten, caldb, calv):
        """Creates a signal representation of this stimulus, in the
        form of a vector of numbers representing electric potential.
        caldb and calv are used to determine the amplitude of the
        signal.

        Must be implemented by subclass

        :param fs: Generation samplerate (Hz) at which this signal will be output
        :type fs: int
        :param atten: actually just 0 for now?
        :param caldb: calibration intensity in dbSPL
        :type caldb: float
        :param calv: calibration voltage that was used to record the intensity provided
        :type calv: float
        """
        raise NotImplementedError

    def verify(self, **kwargs):
        """Checks this component for invalidating conditions

        :returns: str -- message if error, 0 otherwise
        """
        if 'duration' in kwargs:
            if kwargs['duration'] < self._duration:
                return "Window size must equal or exceed stimulus length"
        if self._risefall > self._duration:
            return "Rise and fall times exceed component duration"
        return 0

    def auto_details(self):
        """A collection of the parameter names that are available to
        be set using auto-paramter manipulation. 

        Subclasses should re-implement and add to this list

        :returns: dict<dict> -- {'parametername': {'label':str, 'unit':str, 'min':float, 'max':float},}
        """
        return {'duration':{'unit':'s', 'min':0., 'max':3.},
                'intensity':{'unit':'dB SPL', 'min':0, 'max':120}, 
                'risefall':{'unit':'s', 'min':0, 'max':0.1}}

    def stateDict(self):
        """Saves internal values to be loaded later

        :returns: dict -- {'parametername': value, ...}
        """
        state = {
                'duration' : self._duration,
                'intensity' : self._intensity,
                'risefall' : self._risefall,
                'stim_type' : self.name
                }
        return state

    def loadState(self, state):
        """Loads previously saved values to this component. 

        :param state: return value from `stateDict`
        :type state: dict
        """
        self._duration = state['duration']
        self._intensity = state['intensity']
        self._risefall = state['risefall']

    def serialize(self):
        return cPickle.dumps(self)

    def clean(self):
        pass    

    @staticmethod
    def deserialize(stream):
        return cPickle.loads(stream)

    def __repr__(self):
        return self.__class__.__name__ + ':' + str(self.idnum)

    def __eq__(self, other):
        if self.idnum == other.idnum:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.idnum != other.idnum:
            return True
        else:
            return False
