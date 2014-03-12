import os
import wave

import scipy.io.wavfile as wv
from scipy.signal import chirp
import numpy as np

from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_stimulus import AbstractStimulusComponent
from spikeylab.stim.types.widgets import tone_parameters, silence_parameters
from spikeylab.stim.types.widgets import vocal_parameters
from spikeylab.tools.audiotools import spectrogram, make_tone

from pyqtgraph import GradientEditorItem


COLORTABLE=[]
for i in reversed(range(256)): COLORTABLE.append(QtGui.qRgb(i,i,i))

class Tone(AbstractStimulusComponent):
    foo = None

class PureTone(Tone):
    name = "Pure Tone"
    explore = True
    protocol = True
    _frequency = 5000
    def update_fscale(self, scale):
        print '!updating tone scale'
        self._frequency_details['multiplier'] = scale

    def frequency(self):
        return self._frequency

    def setFrequency(self, freq):
        self._frequency = freq

    def showEditor(self):
        editor = tone_parameters.ToneParameterWidget()
        editor.setComponent(self)
        return editor

    def paint(self, painter, rect, palette):
        if (self._frequency/self._scales[1]) - np.floor(self._frequency/self._scales[1]) > 0.0:
            freq = str(self._frequency/self._scales[1])
        else:
            freq = str(int(self._frequency/self._scales[1]))
        painter.fillRect(rect, palette.base())
        painter.drawText(rect.x()+5, rect.y()+12, rect.width()-5, rect.height()-12, QtCore.Qt.AlignLeft, "Pure Tone")
        painter.fillRect(rect.x()+5, rect.y()+35, rect.width()-10, 20, QtCore.Qt.black)
        painter.drawText(rect.x()+5, rect.y()+80,  freq+ " "+self._labels[1])

    def signal(self, fs, atten, caldb, calv):
        tone = make_tone(self._frequency, self._intensity+atten, self._duration, self._risefall, fs, caldb=caldb, calv=calv)[0]
        return tone

    def stateDict(self):
        state = super(PureTone, self).stateDict()
        state['frequency'] = self._frequency

        return state

    def loadState(self, state):
        super(PureTone,self).loadState(state)
        self._frequency = state['frequency']

    def auto_details(self):
        details = super(PureTone, self).auto_details()
        details['frequency'] = {'label':self._labels[1], 'multiplier':self._scales[1], 'min':0, 'max':200000}
        return details

    def verify(self, **kwargs):
        if 'samplerate' in kwargs:
            if kwargs['samplerate']/2 < self._frequency:
                return "Generation sample rate must be at least twice the stimulus frequency"
        return super(PureTone, self).verify(**kwargs)

class FMSweep(Tone):
    name = "FM Sweep"
    _start_f = 5000
    _stop_f = 1e5
    explore = True

    def signal(self, fs, atten, caldb, calv):
        amp = (10 ** (float(self._intensity+atten-caldb)/20)*calv)
        npts = self._duration*fs
        t = np.arange(npts).astype(float)/fs
        signal = chirp(t, f0=self._start_f, f1=self._stop_f, t1=self._duration)
        signal = ((signal/np.amax(signal))*amp)
        return signal

    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)

    def showEditor(self):
        editor = silence_parameters.NoiseParameterWidget()
        editor.setComponent(self)
        return editor

class Vocalization(AbstractStimulusComponent):
    name = "Vocalization"
    explore = True
    protocol = True
    _filename = None
    _browsedir = os.path.expanduser('~')

    def browsedir(self):
        return self._browsedir

    def setBrowseDir(self, browsedir):
        self._browsedir = browsedir

    def file(self):
        return self._filename

    def samplerate(self):
        if self._filename is not None:
            wf =  wave.open(self._filename)
            fs= wf.getframerate()
            wf.close()
            return fs

    def stateDict(self):
        state = super(Vocalization, self).stateDict()
        state['file'] = self._filename
        state['browsedir'] = self._browsedir
        return state

    def loadState(self, state):
        super(Vocalization,self).loadState(state)
        self._browsedir = state['browsedir']
        self._filename = state['file']

    def setFile(self, fname):
        if fname is not None:
            self._filename = fname

            try:
                sr, wavdata = wv.read(fname)
            except:
                print u"Problem reading wav file"
                raise
            # wavdata = wavdata.astype(float)
            # nfft=512
            # Pxx, freqs, bins, im = specgram(wavdata, NFFT=nfft, Fs=sr, noverlap=int(nfft*0.9), pad_to=nfft*2)

            self._duration = float(len(wavdata))/sr


    def paint(self, painter, rect, palette):

        if self._filename is not None:
            spec, f, bins, fs = spectrogram(self._filename)
            spec = spec.T
            spec = abs(np.fliplr(spec))
            spec_max = np.amax(spec)
            # print np.amax(scaled), np.amin(scaled), scaled.shape, spec_max
            scaled = np.around(spec/(spec_max/255)).astype(int)

            width, height = scaled.shape
            image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
            for x in xrange(width):
                for y in xrange(height):
                    image.setPixel(x,y, COLORTABLE[scaled[x,y]])

            pixmap = QtGui.QPixmap.fromImage(image)
            painter.drawPixmap(rect.x(), rect.y(), rect.width(), rect.height(), pixmap)
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
        editor = vocal_parameters.VocalParameterWidget()
        editor.setComponent(self)
        return editor

    def signal(self, fs, atten, caldb, calv):
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
        max_amp = np.amax(wavdata)
        amp = (10 ** (float(self._intensity+atten-caldb)/20)*calv)
        wavdata = ((wavdata/max_amp)*amp)
        return wavdata

    def auto_details(self):
        details = super(Vocalization, self).auto_details()
        del details['duration']
        return details

    def verify(self, **kwargs):
        if self._filename is None:
            return "Vocalization stimulus without a specified file"
        return 0

class WhiteNoise(AbstractStimulusComponent):
    name = "White Noise"
    explore = True
    # keeps signal same to subsequent signal calls, but limit size
    _noise = np.random.normal(0, 1.0, (5e5,))
    transfer = None

    def signal(self, fs, atten, caldb, calv):
        amp = (10 ** (float(self._intensity+atten-caldb)/20)*calv)
        npts = self._duration*fs
        signal = self._noise[:npts]
        signal = ((signal/np.amax(signal))*amp)
        return signal

    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)

    def showEditor(self):
        editor = silence_parameters.NoiseParameterWidget()
        editor.setComponent(self)
        return editor

    def setTransfer(self, H):
        self.transfer = H

class Silence(AbstractStimulusComponent):
    name = "silence"
    protocol = True
    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)

    def showEditor(self):
        editor = silence_parameters.SilenceParameterWidget()
        editor.setComponent(self)
        return editor

    def signal(self, *args, **kwargs):
        fs = kwargs['fs']
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