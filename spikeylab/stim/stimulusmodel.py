import cPickle
import os

import scipy.misc

from spikeylab.stim.tone_parameters import ToneParameterWidget, SilenceParameterWidget
from spikeylab.stim.vocal_parameters import VocalParameterWidget
from spikeylab.tools.audiotools import spectrogram

import scipy.io.wavfile as wv
# from matplotlib.mlab import specgram
from pylab import specgram

PIXELS_PER_MS = 5

from matplotlib import cm
from PyQt4 import QtGui, QtCore

# COLORTABLE=cm.get_cmap('jet')
COLORTABLE = []
for i in range(16): COLORTABLE.append(QtGui.qRgb(i/4,i,i/2))

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
                itemData = QtCore.QByteArray()
                # dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
                # dataStream << component
                # return dataStream
                # if component.name == 'vocalization':
                #     imagepickle = cPickle.dumps(component._image)
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
        self.segments[index.row()][index.column()] = value

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable| QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


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
    _duration = None # in seconds
    _fs = 400000 # in Hz
    _intensity = 20 # in dB SPL
    _risefall = 0

    # def __init__(self):
    def duration(self):
        return self._duration

    def setDuration(self, dur):
        self._duration = dur

    def intensity(self):
        return self._intensity

    def setIntensity(self, intensity):
        self._intensity = intensity

    def samplerate(self):
        return self._fs

    def setSamplerate(self, fs):
        self._fs = fs
        
    def risefall(self):
        return self._risefall

    def setRisefall(self, risefall):
        self._risefall = risefall    

    def paint(self, painter, rect, palette):
        painter.save()

        image = QtGui.QImage("./ducklings.jpg")
        painter.drawImage(rect,image)

        # set text color
        painter.setPen(QtGui.QPen(QtCore.Qt.black)) 
        painter.drawText(rect, QtCore.Qt.AlignLeft, self.__class__.__name__)

        painter.restore()

    def sizeHint(self):
        width = self._duration * PIXELS_PER_MS * 1000
        return QtCore.QSize(width, 50)

    def showEditor(self):
        raise NotImplementedError


class Tone(AbstractStimulusComponent):
    foo = None

class PureTone(Tone):
    name = "puretone"
    _frequency = 5000

    def frequency(self):
        return self._frequency

    def setFrequency(self, freq):
        self._frequency = freq

    def showEditor(self):
        editor = ToneParameterWidget()
        editor.setComponent(self)
        return editor

    def paint(self, painter, rect, palette):

        painter.drawText(rect.x()+5, rect.y()+12, rect.width()-5, rect.height()-12, QtCore.Qt.AlignLeft, "Pure Tone")
        painter.fillRect(rect.x()+5, rect.y()+35, rect.width()-10, 20, QtCore.Qt.black)
        painter.drawText(rect.x()+5, rect.y()+80, str(self._frequency/1000) + " kHz")

class FMSweep(Tone):
    name = "fmsweep"
    start_frequency = None
    stop_frequency = None

class Vocalization(AbstractStimulusComponent):
    name = "vocalization"
    _filename = None
    _browsedir = os.path.expanduser('~')
    def browsedir(self):
        return self._browsedir

    def setBrowseDir(self, browsedir):
        self._browsedir = browsedir

    def file(self):
        return self._filename

    def setFile(self, fname):
        self._filename = fname

        nfft=512
        try:
            sr, wavdata = wv.read(fname)
        except:
            print u"Problem reading wav file"
            raise
        wavdata = wavdata.astype(float)
        Pxx, freqs, bins, im = specgram(wavdata, NFFT=nfft, Fs=sr, noverlap=int(nfft*0.9), pad_to=nfft*2)

        self._duration = float(len(wavdata))/sr


    def paint(self, painter, rect, palette):

        nfft=512
        try:
            sr, wavdata = wv.read(self._filename)
        except:
            print u"Problem reading wav file"
            raise
        wavdata = wavdata.astype(float)
        Pxx, freqs, bins, im = specgram(wavdata, NFFT=nfft, Fs=sr, noverlap=int(nfft*0.9), pad_to=nfft*2)

        self._duration = float(len(wavdata))/sr

        rows, cols, rgb = im.make_image().as_rgba_str()
        image = QtGui.QImage(rgb, cols, rows, QtGui.QImage.Format_ARGB32)
        pixmap = QtGui.QPixmap(QtGui.QPixmap.fromImage(image))
        painter.drawPixmap(rect, pixmap)

    def showEditor(self):
        editor = VocalParameterWidget()
        editor.setComponent(self)
        return editor

class Noise(AbstractStimulusComponent):
    name = "noise"

class Silence(AbstractStimulusComponent):
    name = "silence"

    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)

    def showEditor(self):
        editor = SilenceParameterWidget()
        editor.setComponent(self)
        return editor

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