from spikeylab.tools.audiotools import calc_spectrum

import test.sample as sample

import numpy as np
import scipy.io.wavfile as wv

import matplotlib.pyplot as plt

def data_func(self, f):
    return 2*np.sin(2*np.pi*f*self.t/len(self.t))

def test_calc_spectrum_even_len_signal():
    n = 100000
    x = np.linspace(0, 2*np.pi, n)
    fq = 15000
    fs = 100000
    y = np.sin(((n/fs)*fq)*x)

    frequencies, spectrum = calc_spectrum(y, fs)

    assert len(spectrum) == len(y)/2 + 1 == len(frequencies)
    assert frequencies[-1] == fs/2
    assert (abs(spectrum - max(spectrum))).argmin() == (abs(frequencies - fq)).argmin()

def test_calc_spectrum_odd_len_signal():
    n = 2000011
    x = np.linspace(0, 2*np.pi, n)
    fq = 15000
    fs = 100000
    y = np.sin(((n/fs)*fq)*x)

    freq_control = np.fft.fftfreq(n, 1/float(fs))
    print 'max freq control', max(freq_control)
    frequencies, spectrum = calc_spectrum(y, fs)
    print 'frequencies', frequencies[0:10], frequencies[-10:], len(frequencies)
    assert len(spectrum) == len(y)/2 + 1 == len(frequencies)
    print "Nyquist", frequencies[-1], fs/2
    assert np.around(frequencies[-1]) == fs/2
    peak_idx = (abs(spectrum - max(spectrum))).argmin()
    freq_idx = (abs(frequencies - fq)).argmin()
    print peak_idx, freq_idx, frequencies[freq_idx] 
    plt.plot(frequencies, spectrum)
    plt.show()
    assert (abs(spectrum - max(spectrum))).argmin() == (abs(frequencies - fq)).argmin()
    assert False