import cPickle
import os
import uuid

import scipy.misc

from spikeylab.stim.tone_parameters import ToneParameterWidget, SilenceParameterWidget
from spikeylab.stim.vocal_parameters import VocalParameterWidget
from spikeylab.tools.audiotools import spectrogram, make_tone
from spikeylab.stim.auto_parameter_modelview import AutoParameterModel

import numpy as np
import scipy.io.wavfile as wv
# from matplotlib.mlab import specgram
from pylab import specgram


from matplotlib import cm
from PyQt4 import QtGui, QtCore

# COLORTABLE=cm.get_cmap('jet')
COLORTABLE = []
for i in range(16): COLORTABLE.append(QtGui.qRgb(i/4,i,i/2))

class StimulusModel(QtCore.QAbstractItemModel):
    """
    Model to represent any stimulus the system will present. 
    Holds all relevant parameters
    """
    def __init__(self, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.nreps = 0
        self.samplerate = 375000
        # 2D array of simulus components track number x component number
        self.segments = [[]]
        # add an empty place to place components into new track
        self.auto_params = AutoParameterModel()

        # reference for what voltage == what intensity
        self.calv = 0.1
        self.caldb = 100

    def setAutoParams(self, params):
        self.auto_params = params

    def autoParams(self):
        return self.auto_params

    def headerData(self, section, orientation, role):
        return ''

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.segments)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            print 'querying column count by parent'
            wholerow = parent.internalPointer()
            return len(wholerow)
        else:
            column_lengths = [len(x) for x in self.segments]
            return max(column_lengths)

    def columnCountForRow(self, row):
        return len(self.segments[row])

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            component = self.segments[index.row()][index.column()]
            return component.__class__.__name__
        elif role == QtCore.Qt.UserRole:  #return the whole python object
            if len(self.segments[index.row()]) > index.column():
                component = self.segments[index.row()][index.column()]
            else:
                component = None
            return component
        elif role == QtCore.Qt.SizeHintRole:
            component = self.segments[index.row()][index.column()]
            return component.duration() #* PIXELS_PER_MS * 1000

    def printStimulus(self):
        """This is for purposes of documenting what was presented"""


    def index(self, row, col, parent=QtCore.QModelIndex()):
        # need to convert row, col to correct element, however still have heirarchy?
        if parent.isValid():
            print 'valid parent', parent.row(), parent.col()
            prow = self.segments.index(parent.internalPointer())
            return self.createIndex(prow, row, self.segments[prow][row])
        else:
            if row < len(self.segments) and col < len(self.segments[row]):
                return self.createIndex(row, col, self.segments[row][col])
            else:
                return QtCore.QModelIndex()

    def parentForRow(self, row):
        # get the whole row
        return self.createIndex(row, -1, self.segments[row])

    def parent(self, index):
        if index.column() == -1:
            return QtCore.QModelIndex()
        else:
            return self.createIndex(index.row(), -1, self.segments[index.row()])

    def insertComponent(self, comp, rowcol=(0,0)):
        parent = self.parentForRow(rowcol[0])
        # convert to index or done already?
        self.beginInsertRows(parent, rowcol[1], rowcol[1])
        parent.internalPointer().insert(rowcol[1], comp)
        self.endInsertRows()

        if len(self.segments[-1]) > 0:
            self.beginInsertRows(QtCore.QModelIndex(), len(self.segments), len(self.segments))
            self.segments.append([])
            self.endInsertRows()

    def removeComponent(self, rowcol):
        parent = self.parentForRow(rowcol[0])

        self.beginRemoveRows(parent, rowcol[1], rowcol[1])
        parent.internalPointer().pop(rowcol[1])
        self.endRemoveRows()

        if len(self.segments[-2]) == 0:
            self.beginRemoveRows(QtCore.QModelIndex(), len(self.segments)-1, len(self.segments)-1)
            self.segments.pop(len(self.segments)-1)
            self.endRemoveRows()

    def indexByComponent(self, component):
        """return a QModelIndex for the given component, or None if
        it is not in the model"""
        for row, rowcontents in enumerate(self.segments):
            if component in rowcontents:
                column = rowcontents.index(component)
                return self.index(row, column)

    def setData(self, index, value):
        # item must already exist at provided index
        self.segments[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable| QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def expandedStim(self):
        """
        Apply the autoparameters to this stimulus and return a list of
        the resulting stimuli
        """
        # initilize array to hold all varied parameters
        params = self.auto_params.allData()
        steps = []
        ntraces = 1
        for p in params:
            steps.append(np.arange(p['start'], p['stop'], p['step']))
            ntraces = ntraces*len(steps[-1])

        varylist = [[steps[ip][itrace % len(steps[ip])] for ip in range(len(params))] for itrace in range(ntraces)]

        # varylist = [[None for x in range(len(params))] for y in range(ntraces)]
        # for ip, param in enumerate(params):
        #     for itrace in range(ntraces):
        #         value = steps[ip][itrace % len(steps[ip])]
        #         varylist[itrace][ip] = value

        # now create the stimuli according to steps
        stim_list = []
        for itrace in range(ntraces):
            for ip, param in enumerate(params):
                comp_inds = self.auto_params.selection(param)
                for index in comp_inds:
                    component = self.data(index, QtCore.Qt.UserRole)
                    component.set(param['parameter'], varylist[itrace][ip])
            # copy of current stim state, or go ahead and turn it into a signal?
            # so then would I want to formulate some doc here as well?
            stim_list.append(self.signal())

        # now reset the components to start value
        for ip, param in enumerate(params):
            comp_inds = self.auto_params.selection(param)
            for index in comp_inds:
                component = self.data(index, QtCore.Qt.UserRole)
                component.set(param['parameter'], varylist[0][ip])

        return stim_list

    def expanded_doc(self):
        """
        JSON/YAML/XML representation of exactly what was presented
        """

    def template_doc(self):
        """
        JSON/YAML/XML template to recreate this stimulus in another session
        """

    def signal(self):
        """Return the current stimulus in signal representation"""
        track_signals = []
        max_db = max([comp.intensity() for t in self.segments for comp in t])
        caldb = 100
        atten = caldb - max_db
        for track in self.segments:
            # nsamples = sum([comp.duration() for comp in track])*self.samplerate
            # track_signal = np.zeros((nsamples,))
            track_list = []
            for component in track:
                track_list.append(component.signal(self.samplerate, atten))
            if len(track_list) > 0:   
                track_signals.append(np.hstack(track_list))

        # track_signals = sorted(track_signals, key=len, reverse=True)
        full_len = len(max(track_signals, key=len))
        total_signal = np.zeros((full_len,))
        for track in track_signals:
            total_signal[0:len(track)] += track

        return total_signal


class AbstractStimulusComponent(object):
    """Represents a single component of a complete summed stimulus"""
    _start_time = None
    _duration = .01 # in seconds
    _intensity = 20 # in dB SPL
    _risefall = 0
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

        painter.fillRect(rect, palette.base())
        painter.drawText(rect.x()+5, rect.y()+12, rect.width()-5, rect.height()-12, QtCore.Qt.AlignLeft, "Pure Tone")
        painter.fillRect(rect.x()+5, rect.y()+35, rect.width()-10, 20, QtCore.Qt.black)
        painter.drawText(rect.x()+5, rect.y()+80, str(self._frequency/1000) + " kHz")

    def signal(self, fs, atten):
        tone = make_tone(self._frequency, self._intensity+atten, self._duration, self._risefall, fs)[0]
        return tone


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
        if fname is not None:
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

        if self._filename is not None:
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
            # Why is the rect not equal to the draw rect seen in GUI?????
            painter.drawPixmap(rect.x(), rect.y(), rect.width()+25, rect.height()+6, pixmap)
        else:
            painter.save()
            # draw a warning symbol
            smallrect = QtCore.QRect(rect.x()+10, rect.y()+10, rect.width()-20, rect.height()-20)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 8))
            painter.drawEllipse(smallrect)
            rad = smallrect.width()/2
            x = rad - (np.cos(np.pi/4)*rad)
            painter.drawLine(smallrect.x()+x, smallrect.y()+x, smallrect.x()+smallrect.width()-x, smallrect.y()+smallrect.height()-x)

            painter.restore()
            
    def showEditor(self):
        editor = VocalParameterWidget()
        editor.setComponent(self)
        return editor

    def signal(self, fs, atten):
        try:
            sr, wavdata = wv.read(self._filename)
        except:
            print u"Problem reading wav file"
            raise
        if fs != sr:
            print 'specified', fs, 'wav file', sr
            raise Exception("specified samplerate does not match wav stimulus")
        # normalize to calibration
        wavdata = wavdata.astype(float)
        print "DANGER vocal wav files Hard-coded calibration 100db 0.1V"
        caldB = 100
        v_at_caldB = 0.1
        max_amp = np.amax(wavdata)
        amp = (10 ** ((self._intensity+atten-caldB)/20)*v_at_caldB)
        wavdata = ((wavdata/max_amp)*amp)
        return wavdata

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

    def signal(self, fs, atten):
        return np.zeros((self._duration*fs,))

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