from spikeylab.tools.audiotools import calc_spectrum, make_tone, spectrogram

import test.sample as sample

import numpy as np
import scipy.io.wavfile as wv

import matplotlib.pyplot as plt

def data_func(self, f):
    return 2*np.sin(2*np.pi*f*self.t/len(self.t))

def test_calc_spectrum_even_len_signal():
    n = 100000
    fq = 15000
    fs = 100000
    # x = np.linspace(0, 2*np.pi, n)
    # y = np.sin(((n/fs)*fq)*x)
    t = np.arange(n)
    y = np.sin(2*np.pi*fq*t/fs)

    frequencies, spectrum = calc_spectrum(y, fs)

    assert len(spectrum) == len(y)/2 + 1 == len(frequencies)
    assert frequencies[-1] == fs/2
    assert (abs(spectrum - max(spectrum))).argmin() == (abs(frequencies - fq)).argmin()

def test_calc_spectrum_odd_len_signal():
    n = 200101
    t = np.arange(n)
    fq = 15000
    fs = 100000
    y = np.sin(2*np.pi*fq*t/fs)

    freq_control = np.fft.fftfreq(n, 1/float(fs))
    print 'max freq control', max(freq_control)
    frequencies, spectrum = calc_spectrum(y, fs)
    print 'frequencies', frequencies[0:10], frequencies[-10:], len(frequencies)
    assert len(spectrum) == len(y)/2 + 1 == len(frequencies)
    print "Nyquist", frequencies[-1], fs/2
    assert np.around(frequencies[-1]) == fs/2
    peak_idx = (abs(spectrum - max(spectrum))).argmin()
    freq_idx = (abs(frequencies - fq)).argmin()
    print peak_idx, freq_idx, frequencies[peak_idx], frequencies[freq_idx] 
    assert (abs(spectrum - max(spectrum))).argmin() == (abs(frequencies - fq)).argmin()

def test_make_tone_regular_at_caldb():
    fq = 15000
    db = 100
    fs = 100000
    dur = 1
    risefall = 0.002
    fs = 100000
    calv = 0.1
    caldb = 100
    npts = fs*dur

    tone, timevals = make_tone(fq, db, dur, risefall, fs, caldb, calv)

    assert len(tone) == npts

    spectrum = np.fft.rfft(tone)
    peak_idx = (abs(spectrum - max(spectrum))).argmin()
    freq_idx = np.around(fq*(float(npts)/fs))
    assert peak_idx == freq_idx

    print 'tone max', np.around(np.amax(tone), 5), calv
    assert np.around(np.amax(tone), 5) == calv

    assert timevals[-1] == dur - (1./fs)

def test_make_tone_irregular():
    fq = 15066
    db = 82
    fs = 200101
    dur = 0.7
    risefall = 0.0015
    fs = 100000
    calv = 0.888
    caldb = 99
    npts = fs*dur

    tone, timevals = make_tone(fq, db, dur, risefall, fs, caldb, calv)

    assert len(tone) == npts

    spectrum = np.fft.rfft(tone)
    peak_idx = (abs(spectrum - max(spectrum))).argmin()
    freq_idx = np.around(fq*(float(npts)/fs))
    assert peak_idx == freq_idx

    print 'intensities', (20 * np.log10(np.amax(tone)/calv)) + caldb, db
    assert np.around((20 * np.log10(np.amax(tone)/calv)) + caldb, 5) == db

    print 'durs', np.around(timevals[-1], 5), dur - (1./fs)
    assert timevals[-1] == dur - (1./fs)

def test_spectrogram_from_file():

    spec, freqs, bins, duration = spectrogram(sample.samplewav())

    # check that duration lies on ms
    assert (duration*1000) % 1 == 0
    print np.amax(spec), np.amin(spec)
    # assert np.all(spec > 0)

def test_spectrogram_from_signal():
    audio = wv.read(sample.samplewav())

    spec, freqs, bins, duration = spectrogram(audio)
    assert (duration*1000) % 1 == 0