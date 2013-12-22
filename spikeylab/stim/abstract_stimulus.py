import uuid
import cPickle

from PyQt4 import QtGui, QtCore

class AbstractStimulusComponent(object):
    """Represents a single component of a complete summed stimulus"""
    _start_time = None
    _duration = .01 # in seconds
    _intensity = 20 # in dB SPL
    _risefall = 0
    name = 'unknown'
    valid = False
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

    def signal(self, fs, atten):
        raise NotImplementedError

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

    def serialize(self):
        return cPickle.dumps(self)

    @staticmethod
    def deserialize(stream):
        return cPickle.loads(stream)

    def __repr__(self):
        return "StimComponent:"  + str(self.idnum)

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
