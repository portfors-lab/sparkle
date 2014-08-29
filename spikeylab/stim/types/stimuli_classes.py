import os, yaml

from scipy.signal import chirp, hann
import numpy as np

from PyQt4 import QtGui, QtCore

from spikeylab.stim.abstract_stimulus import AbstractStimulusComponent
from spikeylab.gui.stim.components import silence_parameters
from spikeylab.gui.stim.components import vocal_parameters
from spikeylab.tools.audiotools import spectrogram, make_tone, audioread, audiorate
from spikeylab.tools.systools import get_src_directory
from spikeylab.tools.exceptions import FileDoesNotExistError

from pyqtgraph import GradientEditorItem

src_dir = get_src_directory()
with open(os.path.join(src_dir,'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
USE_RMS = config['use_rms']

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
        rms = np.sqrt(np.mean(pow(tone,2)))
        # print 'before rms adjust', rms, 'max', np.amax(tone)
        if USE_RMS:
            tone = tone*1.414213562373
        # rms = np.sqrt(np.mean(pow(tone,2)))
        # print 'rms out of tone signal', rms, 'max', np.amax(tone)
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

class FMSweep(AbstractStimulusComponent):
    name = "FM Sweep"
    _start_f = 5000
    _stop_f = 1e5
    explore = True
    protocol = True

    def startFrequency(self):
        return self._start_f

    def stopFrequency(self):
        return self._stop_f

    def setStartFrequency(self, f):
        self._start_f = f

    def setStopFrequency(self, f):
        self._stop_f = f

    def signal(self, fs, atten, caldb, calv):
        amp = (10 ** (float(self._intensity+atten-caldb)/20)*calv)
        npts = self._duration*fs
        t = np.arange(npts).astype(float)/fs
        signal = chirp(t, f0=self._start_f, f1=self._stop_f, t1=self._duration)
        signal = ((signal/np.amax(signal))*amp)
        if USE_RMS:
            signal = signal*1.414213562373

        if self._risefall > 0:
            rf_npts = int(self._risefall * fs)
            wnd = hann(rf_npts*2) # cosine taper
            signal[:rf_npts] = signal[:rf_npts] * wnd[:rf_npts]
            signal[-rf_npts:] = signal[-rf_npts:] * wnd[rf_npts:]
        return signal

    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)

    def auto_details(self):
        details = super(FMSweep, self).auto_details()
        details['start_f'] = {'label':self._labels[1], 'multiplier':self._scales[1], 'min':0, 'max':200000, 'text': "Start Frequency"}
        details['stop_f'] = {'label':self._labels[1], 'multiplier':self._scales[1], 'min':0, 'max':200000, 'text': "Stop Frequency"}
        return details

    def loadState(self, state):
        super(FMSweep,self).loadState(state)
        self._start_f = state['start_f']
        self._stop_f = state['stop_f']

    def stateDict(self):
        state = super(FMSweep, self).stateDict()
        state['start_f'] = self._start_f
        state['stop_f'] = self._stop_f
        return state

class Vocalization(AbstractStimulusComponent):
    name = "Vocalization"
    explore = True
    protocol = True
    _filename = None
    _browsedir = os.path.expanduser('~')
    _cached_pixmap = None # for faster drawing

    def browsedir(self):
        return self._browsedir

    def setBrowseDir(self, browsedir):
        self._browsedir = browsedir

    def file(self):
        return self._filename

    def samplerate(self):
        if self._filename is not None:
            return audiorate(self._filename)

    def stateDict(self):
        state = super(Vocalization, self).stateDict()
        state['file'] = self._filename
        state['browsedir'] = self._browsedir
        return state

    def loadState(self, state):
        super(Vocalization,self).loadState(state)

        browsedir = state['browsedir']
        fname = state['file']

        # error will occur later if unset
        if os.path.isdir(browsedir):
            self._browsedir = browsedir
        if fname is not None and os.path.isfile(fname):
            self._filename = fname
            
        # if not os.path.isdir(browsedir):
        #     raise FileDoesNotExistError(browsedir)
        # self._browsedir = browsedir

        # if not os.path.isfile(fname):
        #     raise FileDoesNotExistError(fname)
        # self._filename = fname

    def setFile(self, fname):
        if fname is not None:
            self._filename = fname

            sr, wavdata = audioread(self._filename)

            # round to the nearest ms
            duration = np.trunc((float(len(wavdata))/sr)*1000)/1000

            self._duration = duration
            self._cached_pixmap = None

    def paint(self, painter, rect, palette):
        if self._filename is not None:
            if self._cached_pixmap is None:
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
                self._cached_pixmap = pixmap
            else:
                pixmap = self._cached_pixmap
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
        sr, wavdata = audioread(self._filename)
        if fs != sr:
            print 'specified', fs, 'wav file', sr
            raise Exception("specified samplerate does not match wav stimulus")

        #truncate to nears ms
        duration = float(len(wavdata))/sr
        # print 'duration {}, desired {}'.format(duration, np.trunc(duration*1000)/1000)
        desired_npts = int((np.trunc(duration*1000)/1000)*sr)
        # print 'npts. desired', len(wavdata), desired_npts
        wavdata = wavdata[:desired_npts]

        if USE_RMS:
            amp_scale = np.sqrt(np.mean(pow(wavdata,2)))
        else:
            amp_scale = np.amax(wavdata)
        amp = (10 ** (float(self._intensity+atten-caldb)/20)*calv)
        signal = ((wavdata/amp_scale)*amp)

        if self._risefall > 0:
            rf_npts = int(self._risefall * fs)
            wnd = hann(rf_npts*2) # cosine taper
            signal[:rf_npts] = signal[:rf_npts] * wnd[:rf_npts]
            signal[-rf_npts:] = signal[-rf_npts:] * wnd[rf_npts:]
            
        return signal

    def auto_details(self):
        details = super(Vocalization, self).auto_details()
        del details['duration']
        details['file'] = {'label':'Edit from component dialog'}
        return details

    def verify(self, **kwargs):
        if self._filename is None:
            return "Vocalization stimulus without a specified file"
        return 0

    def clean(self):
        self._cached_pixmap = None

    def setDuration(self, dur):
        raise Exception("Duration not settable on recordings")

    def set(self, param, value):
        if param == 'duration':
            raise Exception("Duration not settable on recordings")
        super(Vocalization, self).set(param, value)

class WhiteNoise(AbstractStimulusComponent):
    name = "White Noise"
    explore = True
    # keeps signal same to subsequent signal() calls
    _noise = np.random.normal(0, 1.0, (15e5,))
    _phase = np.random.uniform(0.0, 2.0*np.pi,size=15e5)
    transfer = None
    _start_f = float(5000)
    _stop_f = float(1e5)

    def signal(self, fs, atten, caldb, calv):
        npts = self._duration*fs

        # based on Brandon's code:
        # nFreqPts = 1+npts/2        
        # mag = np.zeros(shape=(nFreqPts,),dtype=np.float32)
        # f0 = np.ceil(self._start_f/(float(fs)/npts))
        # f1 = np.floor(self._stop_f/(float(fs)/npts))
        # mag[f0:f1] = 1.0
        # phase = self._phase[:nFreqPts]
        # spec = np.empty(shape=(nFreqPts,),dtype=np.complex64)
        # spec.real = mag * np.cos(phase)
        # spec.imag = mag * np.sin(phase)
        # spec[0] = 0 # DC
        # signal = np.empty(shape=(npts,),dtype=np.float32) # needs to be 32-bit float
        # signal = np.fft.irfft(spec)

        signal = self._noise[:npts]
        
        amp = (10 ** (float(self._intensity+atten-caldb)/20)*calv)
        if USE_RMS:
            amp_scale = np.sqrt(np.mean(pow(signal,2)))
        else:
            amp_scale = np.amax(signal)

        signal = ((signal/amp_scale)*amp)
        # print 'signal max', np.amax(abs(signal)), amp, amp_scale, 'rms', np.sqrt(np.mean(signal**2))
        return signal

    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)

    def setTransfer(self, H):
        self.transfer = H

class Silence(AbstractStimulusComponent):
    name = "silence"
    protocol = True
    _risefall = 0
    _intensity = 0
    def paint(self, painter, rect, palette):
        mid = rect.y() + (rect.height()/2)
        painter.drawLine(rect.x()+5, mid, rect.x()+rect.width()-10, mid)

    def auto_details(self):
        details = super(Silence, self).auto_details()
        less_details = {'duration': details['duration']}
        return less_details

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

