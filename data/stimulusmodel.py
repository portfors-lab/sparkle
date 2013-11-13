import cPickle

from PyQt4 import QtGui, QtCore

from audiolab.tools.langtools import enum

PIXELS_PER_MS = 5


class StimulusModel(QtCore.QAbstractTableModel):
    """Model to represent a unique stimulus, holds all relevant parameters"""
    def __init__(self, segments=[[]], parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.nreps = 0
        # 2D array of simulus components track number x component number
        self.segments = segments
        auto_params = []

    def headerData(self, section, orientation, role):
        return ''

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.segments)

    def columnCount(self, parent=QtCore.QModelIndex()):
        column_lengths = [len(x) for x in self.segments]
        return max(column_lengths)

    def columnCountForRow(self, row):
        return len(self.segments[row])

    def data(self, index, role):
        # print 'calling data!', role
        if role == QtCore.Qt.DisplayRole:
            component = self.segments[index.row()][index.column()]
            # do I need anything here?
            return component.__class__.__name__
        elif role == QtCore.Qt.UserRole:  #return the whole python object
            # print '!!userrole!!'
            if len(self.segments[index.row()]) > index.column():
                component = self.segments[index.row()][index.column()]
                component = QtCore.QVariant(cPickle.dumps(component))
            else:
                component = None
            return component
        elif role == QtCore.Qt.SizeHintRole:
            component = self.segments[index.row()][index.column()]
            return component.duration() * PIXELS_PER_MS * 1000
        elif role == 33:
            component = self.segments[index.row()][index.column()]
            return component

    def printStimulus(self):
        """This is for purposes of documenting what was presented"""

    def insertComponent(self, comp, index=(0,0)):
        # sizes = [len(x) for x in self.segments]
        # print 'add at', index, sizes
        if index[0] > len(self.segments)-1:
            self.segments.append([comp])
        else:
            self.segments[index[0]].insert(index[1], comp)

    def removeComponent(self, index):
        self.segments[index[0]].pop(index[1])

    def setData(self, index, value):
        print 'SET DATA MAN!', value.intensity()
        self.segments[index.row()][index.column()] = value

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable| QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

# class TrackModel(QtCore.QAbstractListModel):

#     def __init__(self, segments=[], parent = None):
#         QtCore.QAbstractListModel.__init__(self, parent)
#         self._segments = segments

#     def data(self, index, role):

class AutoParameter():
    """Hold information for parameter modification loop"""
    components = []
    parameter = ""
    delta = None
    stop_type = 0 # 0 : stop time, 1 : N times
    stop_value = None

class AbstractStimulusComponent(object):
    """Represents a single component of a complete summed stimulus"""
    _start_time = None
    _duration = None
    _fs = None
    _intensity = None
    _risefall = None

    # def __init__(self):
    def duration(self):
        return self._duration

    def setDuration(self, dur):
        self._duration = dur

    def paint(self, painter, rect, palette, editMode):
        painter.save()

        image = QtGui.QImage("./ducklings.jpg)")
        painter.drawImage(0,0,image)

        painter.drawRect(rect)

        # set text color
        painter.setPen(QPen(Qt.black)) 
        text = 'cute ducks!'
        painter.drawText(5, 5, text)

        painter.restore()

    def sizeHint(self):
        width = self._duration * PIXELS_PER_MS*1000
        return QtCore.QSize(width, 50)

    def intensity(self):
        return self._intensity

    def setIntensity(self, intensity):
        self._intensity = intensity

    def showEditor(self):
        raise NotImplementedError

class Tone(AbstractStimulusComponent):
    foo = None

class PureTone(Tone):
    name = "puretone"
    frequency = None

class FMSweep(Tone):
    name = "fmsweep"
    start_frequency = None
    stop_frequency = None

class Vocalization(AbstractStimulusComponent):
    name = "vocalization"
    filename = None

class Noise(AbstractStimulusComponent):
    name = "noise"

class Silence(AbstractStimulusComponent):
    name = "silence"

class Modulation(AbstractStimulusComponent):
    modulation_frequency = None

class SAM(Modulation):
    """Sinusodal Amplitude Modulation"""
    name = "sam"

class SquareWaveModulation(Modulation):
    name = "squaremod"

class SFM(AbstractStimulusComponent):
    name = "sfm"

class Ripples(AbstractStimulusComponent):
    name = "ripples"