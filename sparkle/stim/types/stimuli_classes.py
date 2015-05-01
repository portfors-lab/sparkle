import logging
import ntpath
import os

import numpy as np
import yaml
from scipy.signal import chirp, hann, square, butter, lfilter, buttord

from sparkle.stim.abstract_component import AbstractStimulusComponent
from sparkle.tools.audiotools import audiorate, audioread, make_tone, \
    signal_amplitude
from sparkle.tools.exceptions import FileDoesNotExistError


class PureTone(AbstractStimulusComponent):
    name = "Pure Tone"
    explore = True
    protocol = True
    _frequency = 5000
    def frequency(self):
        return self._frequency

    def setFrequency(self, freq):
        self._frequency = freq

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
        details['frequency'] = {'unit':'Hz', 'min':0, 'max':200000}
        return details

    def verify(self, **kwargs):
        if 'samplerate' in kwargs:
            if kwargs['samplerate']/2 < self._frequency:
                return "Generation sample rate must be at least twice the stimulus frequency"
        return super(PureTone, self).verify(**kwargs)

class SquareWave(PureTone):
    name = "Square Wave"
    _frequency = 50
    _amplitude = 1

    def signal(self, fs, atten, caldb, calv):
        npts = int(self._duration * fs)
        t = np.linspace(0, self._duration, npts)
        sig = square(2 * np.pi * self._frequency * t)
        sig = sig * (self._amplitude/2) + (self._amplitude/2)
        return sig

    def auto_details(self):
        details = super(SquareWave, self).auto_details()
        del details['risefall']
        del details['intensity']
        details['amplitude'] = {'unit': 'V', 'min': -10, 'max': 10.}
        return details

    def loadState(self, state):
        super(SquareWave,self).loadState(state)
        self._amplitude = state['amplitude']

    def stateDict(self):
        state = super(SquareWave, self).stateDict()
        state['amplitude'] = self._amplitude
        return state

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
        amp = self.amplitude(caldb, calv)
        npts = self._duration*fs
        t = np.arange(npts).astype(float)/fs
        signal = chirp(t, f0=self._start_f, f1=self._stop_f, t1=self._duration)
        amp_scale = signal_amplitude(signal, fs)
        signal = ((signal/amp_scale)*amp)

        if self._risefall > 0:
            rf_npts = int(self._risefall * fs) / 2
            wnd = hann(rf_npts*2) # cosine taper
            signal[:rf_npts] = signal[:rf_npts] * wnd[:rf_npts]
            signal[-rf_npts:] = signal[-rf_npts:] * wnd[rf_npts:]
        return signal

    def auto_details(self):
        details = super(FMSweep, self).auto_details()
        details['start_f'] = { 'unit':'Hz', 'min':0, 'max':200000, 'text': "Start Frequency"}
        details['stop_f'] = {'unit':'Hz', 'min':0, 'max':200000, 'text': "Stop Frequency"}
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
    paths = []

    def browsedir(self):
        return self._browsedir

    def setBrowseDir(self, browsedir):
        self._browsedir = browsedir

    def file(self):
        if self._filename is not None and self._findFile():
            return self._filename
        else:
            return None

    def samplerate(self):
        if self._filename is not None and self._findFile():
            return audiorate(self._filename)

    def stateDict(self):
        state = super(Vocalization, self).stateDict()
        state['filename'] = self._filename
        state['browsedir'] = self._browsedir
        return state

    def loadState(self, state):
        super(Vocalization,self).loadState(state)

        browsedir = state['browsedir']
        fname = state['filename']

        if os.path.isdir(browsedir):
            self._browsedir = browsedir

        self._filename = fname
        if fname is None:
            logger = logging.getLogger('main')
            logger.warn('Vocalization loaded with no file defined')
        # if not os.path.isdir(browsedir):
        #     raise FileDoesNotExistError(browsedir)
        # self._browsedir = browsedir

        # if not os.path.isfile(fname):
        #     raise FileDoesNotExistError(fname)
        # self._filename = fname

    def setFile(self, fname):
        if fname is not None:
            self._filename = fname

            fs, wavdata = audioread(self._filename)

            # round to the nearest ms
            duration = np.trunc((float(len(wavdata))/fs)*1000)/1000

            self._duration = duration

    def _findFile(self):
        if os.path.isfile(self._filename):
            return True
        # If we are reviewing data, vocal files may not be in original
        # location. Search paths for filename, use ntpath to be able 
        # to pick apart windows style paths on mac/linux
        basename = ntpath.basename(self._filename)
        for path in self.paths:
            if os.path.isfile(os.path.join(path, basename)):
                self.setFile(os.path.join(path, basename))
                return True
        logger = logging.getLogger('main')
        logger.warn('File: {} not found'.format(basename))
        return False

    def signal(self, fs, atten, caldb, calv):
        if self._filename is None:
            # allow lack of file to not cause error, catch in GUI when necessary?
            logger = logging.getLogger('main')
            logger.warn('Vocalization signal request without a file')
            return np.array([0,0])

        if not self._findFile():
            return np.array([0,0])

        fs, wavdata = audioread(self._filename)
        if fs != fs:
            print 'specified', fs, 'wav file', fs
            raise Exception("specified samplerate does not match wav stimulus")

        #truncate to nears ms
        duration = float(len(wavdata))/fs
        # print 'duration {}, desired {}'.format(duration, np.trunc(duration*1000)/1000)
        desired_npts = int((np.trunc(duration*1000)/1000)*fs)
        # print 'npts. desired', len(wavdata), desired_npts
        wavdata = wavdata[:desired_npts]

        amp_scale = signal_amplitude(wavdata, fs)

        signal = ((wavdata/amp_scale)*self.amplitude(caldb, calv))

        if self._risefall > 0:
            rf_npts = int(self._risefall * fs) / 2
            wnd = hann(rf_npts*2) # cosine taper
            signal[:rf_npts] = signal[:rf_npts] * wnd[:rf_npts]
            signal[-rf_npts:] = signal[-rf_npts:] * wnd[rf_npts:]
            
        return signal

    def auto_details(self):
        details = super(Vocalization, self).auto_details()
        del details['duration']
        details['filename'] = {'label':'Edit from component dialog'}
        return details

    def verify(self, **kwargs):
        if self._filename is None:
            return "Vocalization stimulus without a specified file"
        return 0

    def setDuration(self, dur):
        raise Exception("Duration not settable on recordings")

    def set(self, param, value):
        if param == 'duration':
            raise Exception("Duration not settable on recordings")
        super(Vocalization, self).set(param, value)

class WhiteNoise(AbstractStimulusComponent):
    name = "White Noise"
    explore = True
    protocol = True
    # keeps signal same to subsequent signal() calls
    _noise = np.random.normal(0, 1.0, (15e5,))

    def signal(self, fs, atten, caldb, calv):
        npts = self._duration*fs

        signal = self._noise[:npts]
        
        amp = self.amplitude(caldb, calv)
        amp_scale = signal_amplitude(signal, fs)

        signal = ((signal/amp_scale)*amp)

        if self._risefall > 0:
            rf_npts = int(self._risefall * fs) / 2
            wnd = hann(rf_npts*2) # cosine taper
            signal[:rf_npts] = signal[:rf_npts] * wnd[:rf_npts]
            signal[-rf_npts:] = signal[-rf_npts:] * wnd[rf_npts:]
            
        # print 'signal max', np.amax(abs(signal)), amp, amp_scale, 'rms', np.sqrt(np.mean(signal**2))
        return signal

class Silence(AbstractStimulusComponent):
    name = "silence"
    protocol = True
    _risefall = 0
    _intensity = 0

    def auto_details(self):
        details = super(Silence, self).auto_details()
        less_details = {'duration': details['duration']}
        return less_details

    def signal(self, *args, **kwargs):
        fs = kwargs['fs']
        return np.zeros((self._duration*fs,))

class NoStim(AbstractStimulusComponent):
    name = "OFF"
    explore = True
    def signal(self, fs, atten, caldb, calv):
        return [0,0]

    def auto_details(self):
        return {}

class BandNoise(AbstractStimulusComponent):
    name = "Band noise"
    explore = True
    protocol = True
    # keeps signal same to subsequent signal() calls
    _noise = np.random.normal(0, 1.0, (15e5,))
    _center_frequency = 20000
    _width = 1.0 # octave = 1/_width

    def signal(self, fs, atten, caldb, calv):
        npts = self._duration*fs
        # start with full spectrum white noise and band-pass to get desired 
        # frequency range
        signal = self._noise[:npts]
        
        # band frequency cutoffs
        delta = 10**(3./(10.*(2*self._width)))
        low_freq = self._center_frequency / delta
        high_freq = self._center_frequency * delta
        # scipy butter function wants frequencies normalized between 0. and 1.
        nyquist = fs/2.
        low_normed = low_freq / nyquist
        high_normed = high_freq / nyquist

        order, wn = buttord([low_normed, high_normed], [low_normed-0.05, high_normed+0.05], 1, 40)

        # print 'CUTOFFS', low_freq, high_freq
        # print 'ORDER WN', order, wn, low_normed, high_normed

        b, a = butter(order, wn, btype='band')
        signal = lfilter(b, a, signal)

        if self._risefall > 0:
            rf_npts = int(self._risefall * fs) / 2
            wnd = hann(rf_npts*2) # cosine taper
            signal[:rf_npts] = signal[:rf_npts] * wnd[:rf_npts]
            signal[-rf_npts:] = signal[-rf_npts:] * wnd[rf_npts:]

        return signal

    def auto_details(self):
        details = super(BandNoise, self).auto_details()
        details['center_frequency'] = { 'unit':'Hz', 'min':0, 'max':200000, 'text': "Center Frequency"}
        details['width'] = { 'unit':'Ocatve', 'min':0.001, 'max':100, 'text': "Band Width 1/"}
        return details

    def loadState(self, state):
        super(BandNoise,self).loadState(state)
        self._center_frequency = state['center_frequency']
        self._width = state['width']

    def stateDict(self):
        state = super(BandNoise, self).stateDict()
        state['center_frequency'] = self._center_frequency
        state['width'] = self._width
        return state

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
