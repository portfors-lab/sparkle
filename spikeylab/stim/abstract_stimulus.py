import uuid
import cPickle

from PyQt4 import QtGui, QtCore

class AbstractStimulusComponent(object):
    """Represents a single component of a complete summed stimulus"""
    name = 'unknown'
    protocol = False
    explore = False
    _start_time = None
    _duration = .01 # in seconds
    _intensity = 20 # in dB SPL
    _risefall = 0.003
    _scales = [0.001, 1000] # time, frequency scaling factors
    _labels = ['ms', 'kHz']
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

    def paint(self, painter, rect, palette):
        painter.save()

        image = QtGui.QImage("./default.jpg")
        painter.drawImage(rect,image)

        # set text color
        painter.setPen(QtGui.QPen(QtCore.Qt.black)) 
        painter.drawText(rect, QtCore.Qt.AlignLeft, self.__class__.__name__)

        painter.restore()

    def showEditor(self):
        raise NotImplementedError

    def signal(self, **kwargs):
        """kwargs must include: fs and optionally include 
        atten, caldb, calv depending on stimulus type"""
        raise NotImplementedError

    def verify(self, **kwargs):
        if self._risefall > self._duration/2:
            return "Rise and fall times exceed component duration"
        return 0

    def auto_details(self):
        """A list of the parameter names that are available to
        be set using auto-paramter manipulation. Subclasses should
        reimplement and add to this list"""
        return {'duration':{'label':self._labels[0], 'multiplier':self._scales[0], 'min':0.001, 'max':1},
                'intensity':{'label': 'db SPL', 'multiplier':1, 'min':0, 'max':100}, 
                'risefall':{'label':self._labels[0], 'multiplier':self._scales[0], 'min':0, 'max':0.1}}

    def stateDict(self):
        state = {
                'duration' : self._duration,
                'intensity' : self._intensity,
                'risefall' : self._risefall
                }
        return state

    def loadState(self, state):
        self._duration = state['duration']
        self._intensity = state['intensity']
        self._risefall = state['risefall']

    def update_fscale(self, scale):
        self._scales[1] = scale
        if scale == 1000:
            self._labels[1] = 'kHz'
        elif scale == 1:
            self._labels[1] = 'Hz'
        else:
            raise Exception(u"Invalid frequency scale")

    def update_tscale(self, scale):
        self._scales[0] = scale
        if scale == 0.001:
            self._labels[0] = 'ms'
        elif scale == 1:
            self._labels[0] = 's'
        else:
            raise Exception(u"Invalid time scale")

    def serialize(self):
        return cPickle.dumps(self)

    @staticmethod
    def deserialize(stream):
        return cPickle.loads(stream)

    def __repr__(self):
        return "StimComponent:" + str(self.idnum)

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
