import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wv
import yaml
from nose.tools import raises
from numpy.testing import assert_almost_equal, assert_array_almost_equal, \
    assert_array_equal
from scipy import signal
from scipy.stats import linregress

import sparkle.tools.audiotools as tools
import test.sample as sample
from sparkle.tools.systools import get_src_directory


def data_func(t, f):
    return 2*np.sin(2*np.pi*f*t/len(t))

def test_calc_db_0_gain():
    ref = 1.0
    val = 1.0
    result = tools.calc_db(val, ref)
    assert result == 0

def test_calc_db_negative_gain():
    ref = 1.0
    val = 0.1
    result = tools.calc_db(val, ref)
    assert result == -20

def test_calc_db_positive_gain():
    ref = 0.1
    val = 1.0
    result = tools.calc_db(val, ref)
    assert result == 20

def test_calc_db_SPL():
    mphone_sensitivity = 0.004
    result = tools.calc_db(mphone_sensitivity, mphone_sensitivity, 94)
    assert result == 94

def test_calc_db_zeros():
    ref = 0.0
    val = 0.0
    result = tools.calc_db(val, ref)
    assert result is np.nan

def test_calc_db_zero_ref_peak():
    ref = 0.0
    val = 1.0
    result = tools.calc_db(val, ref)
    assert result is np.nan

def test_calc_spectrum_even_len_signal():
    n = 100000
    fq = 15000
    fs = 100000
    # x = np.linspace(0, 2*np.pi, n)
    # y = np.sin(((n/fs)*fq)*x)
    t = np.arange(n)
    y = np.sin(2*np.pi*fq*t/fs)

    frequencies, spectrum = tools.calc_spectrum(y, fs)
    # print len(spectrum) , len(y)/2 + 1 , len(frequencies)

    assert len(spectrum) == len(frequencies)
    assert np.around(frequencies[-1]) == fs/2
    assert (abs(spectrum - max(spectrum))).argmin() == (abs(frequencies - fq)).argmin()

def test_calc_spectrum_odd_len_signal():
    n = 200101
    t = np.arange(n)
    fq = 15000
    fs = 100000
    y = np.sin(2*np.pi*fq*t/fs)

    freq_control = np.fft.fftfreq(n, 1/float(fs))
    print 'max freq control', max(freq_control)
    frequencies, spectrum = tools.calc_spectrum(y, fs)
    print 'frequencies', frequencies[0:10], frequencies[-10:], len(frequencies)
    assert len(spectrum) == len(frequencies)
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
    calv = 0.1
    caldb = 100
    npts = fs*dur

    tone, timevals = tools.make_tone(fq, db, dur, risefall, fs, caldb, calv)

    assert len(tone) == npts
    assert len(timevals) == npts

    spectrum = np.fft.rfft(tone)
    peak_idx = (abs(spectrum - max(spectrum))).argmin()
    freq_idx = np.around(fq*(float(npts)/fs))
    assert peak_idx == freq_idx

    if tools.USE_RMS is True:
        print 'tone max', np.around(np.amax(tone), 5), calv*np.sqrt(2)
        assert np.around(np.amax(tone), 5) == np.around(calv*np.sqrt(2),5)
    else:
        assert np.around(np.amax(tone), 5) == calv

    assert timevals[-1] == dur - (1./fs)

def test_make_tone_irregular():
    fq = 15066
    db = 82
    fs = 200101
    dur = 0.7
    risefall = 0.0015
    calv = 0.888
    caldb = 99
    npts = int(fs*dur)

    tone, timevals = tools.make_tone(fq, db, dur, risefall, fs, caldb, calv)

    print 'lens', npts, len(tone), len(timevals)
    assert len(tone) == npts
    assert len(timevals) == npts

    spectrum = np.fft.rfft(tone)
    peak_idx = (abs(spectrum - max(spectrum))).argmin()
    freq_idx = np.around(fq*(float(npts)/fs))
    assert peak_idx == freq_idx

    print 'intensities', (20 * np.log10(tools.signal_amplitude(tone, fs)/calv)) + caldb, db
    assert np.around((20 * np.log10(tools.signal_amplitude(tone, fs)/calv)) + caldb, 1) == db

    print 'durs', np.around(timevals[-1], 5), dur - (1./fs)
    assert dur - 2*(1./fs) < timevals[-1] <= dur - (1./fs)

def test_tone_zero_duration():
    fq = 15000
    db = 100
    fs = 100000
    dur = 0
    risefall = 0
    calv = 0.1
    caldb = 100

    tone, timevals = tools.make_tone(fq, db, dur, risefall, fs, caldb, calv)

    assert len(tone) == 0
    assert len(timevals) ==0

@raises(ValueError)
def test_tone_bad_risefall():
    fq = 15000
    db = 100
    fs = 100000
    dur = 0.1
    risefall = 0.11
    calv = 0.1
    caldb = 100

    tone, timevals = tools.make_tone(fq, db, dur, risefall, fs, caldb, calv)

@raises(ValueError)
def test_tone_bad_samplerate():
    fq = 15000
    db = 100
    fs = 0
    dur = 0.1
    risefall = 0.01
    calv = 0.1
    caldb = 100

    tone, timevals = tools.make_tone(fq, db, dur, risefall, fs, caldb, calv)

@raises(ValueError)
def test_tone_bad_caldb():
    fq = 15000
    db = 100
    fs = 100000
    dur = 0.1
    risefall = 0.01
    calv = 0.1
    caldb = 0

    tone, timevals = tools.make_tone(fq, db, dur, risefall, fs, caldb, calv)

def test_spectrogram_from_file():
    spec, freqs, bins, duration = tools.spectrogram(sample.samplewav())

    # check that duration lies on ms
    assert (duration*1000) % 1 == 0
    print np.amax(spec), np.amin(spec)
    # assert np.all(spec > 0)

def test_spectrogram_from_signal():
    audio = wv.read(sample.samplewav())

    spec, freqs, bins, duration = tools.spectrogram(audio)
    assert (duration*1000) % 1 == 0

def test_spectrogram_from_file_windows():
    windows = ['hanning', 'hamming', 'bartlett', 'blackman', None]
    for win in windows:
        yield spec_for_window, win

@raises(IOError)
def test_spectrogram_bad_file():
    x = tools.spectrogram('doesnotexist')

def spec_for_window(win):
    spec, freqs, bins, duration = tools.spectrogram(sample.samplewav(), window=win)
    assert (duration*1000) % 1 == 0

def test_spec_overlap():
    audio = wv.read(sample.samplewav())

    spec, freqs, bins0, duration0 = tools.spectrogram(audio, overlap=0)
    spec, freqs, bins50, duration50 = tools.spectrogram(audio, overlap=50)
    spec, freqs, bins99, duration99 = tools.spectrogram(audio, overlap=99)

    assert len(bins0) < len(bins50) < len(bins99)
    assert duration0 == duration50 == duration99

def test_attenuation_curve():
    fs = 5e5
    duration = 0.2
    npts = duration*fs
    t = np.arange(npts).astype(float)/fs

    # add linear drop to get log atten curve
    desired_signal = signal.chirp(t, f0=5000, f1=1e5, t1=duration)
    received_signal = desired_signal*np.linspace(10, 1, npts)

    atten = tools.attenuation_curve(desired_signal, received_signal, fs, 5000, smooth_pts=99)
    atten_range = np.amax(atten[100:20000]) - np.amin(atten[100:20000])

    assert np.around(atten_range) == 20
    assert np.around(atten[20000]) == 20
    assert atten[1000] == 0

def xtest_multiply_frequencies():
    fs = 5e5
    duration = 0.2
    npts = duration*fs
    t = np.arange(npts).astype(float)/fs
    
    frange = [5000, 100000]
    desired_signal = signal.chirp(t, f0=5000, f1=1e5, t1=duration)
    freqs = np.arange(npts/2 + 1)/(float(npts)/fs)
    f0 = (np.abs(freqs-frange[0])).argmin()
    f1 = (np.abs(freqs-frange[1])).argmin()
    atten = np.zeros(npts/2 + 1)
    atten[f0:f1] = np.linspace(0, 20, len(atten[f0:f1]))

    adjusted_signal = tools.multiply_frequencies(desired_signal, fs, frange, freqs, atten)

    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.plot(freqs,atten)
    # plt.plot(adjusted_signal)
    # plt.show()
    assert adjusted_signal.shape == desired_signal.shape
    print 'maxes', np.amax(adjusted_signal) / np.amax(desired_signal)
    assert np.around(np.amax(adjusted_signal) / np.amax(desired_signal)) == 10

def xtest_calibrate_signal():
    fs = 5e5
    duration = 0.2
    npts = duration*fs
    t = np.arange(npts).astype(float)/fs

    frange = [5000, 100000]
    # add linear drop to get log atten curve
    desired_signal = signal.chirp(t, f0=5000, f1=1e5, t1=duration)
    received_signal = desired_signal*np.linspace(1, 0.1, npts)

    calibrated_signal = tools.calibrate_signal(desired_signal, received_signal, fs, frange)

    plt.plot(desired_signal)
    plt.figure()
    plt.plot(calibrated_signal)
    plt.show()

    assert calibrated_signal.shape == desired_signal.shape
    print 'signal max', np.amax(calibrated_signal)
    assert np.amax(calibrated_signal) == 10

def test_impulse_response_truncation_length():
    fs = 5e5
    duration = 0.2
    npts = int(duration*fs)

    frange = [5000, 100000]
    freqs = np.arange(npts/2 + 1)/(float(npts)/fs)
    f0 = (np.abs(freqs-frange[0])).argmin()
    f1 = (np.abs(freqs-frange[1])).argmin()
    atten = np.zeros(npts/2 + 1)
    atten[f0:f1] = np.linspace(0, 20, len(atten[f0:f1]))

    ir = tools.impulse_response(fs, atten, freqs, frange, filter_len=1024)
    assert len(ir) == 1024

    ir = tools.impulse_response(fs, atten, freqs, frange, filter_len=10000)
    assert len(ir) == 10000

    ir = tools.impulse_response(fs, atten, freqs, frange, filter_len=npts)
    assert len(ir) == npts

    ir = tools.impulse_response(fs, atten, freqs, frange, filter_len=npts+1000)
    assert len(ir) == npts

def test_impulse_response_high_pass():
    fs = 5e5
    duration = 0.2
    npts = int(duration*fs)

    freqs = np.arange(npts/2 + 1)/(float(npts)/fs)

    pass_band = np.zeros(npts/2 + 1)
    pass_band[len(pass_band)/2:] = 1

    ir = tools.impulse_response(fs, pass_band, freqs, [freqs[0], freqs[-1]], filter_len=2**14, db=False)

    # w, h = signal.freqz(ir)
    # plt.plot(w, abs(h))
    # plt.show()

    width = 0.05 # the width of the window used in impulse_response
    # Check the gain at a few samples where we know it should be approximately 0 or 1.
    freq_samples = np.array([0.0, 0.25, 0.5-width/2, 0.5+width/2, 0.75, 1.0-width])
    freqs, response = signal.freqz(ir, worN=np.pi*freq_samples)
    assert_array_almost_equal(np.abs(response),
                                [0.0, 0.0, 0.0, 1.0, 1.0, 1.0], decimal=5)

def test_impulse_response_low_pass():
    fs = 5e5
    duration = 0.2
    npts = int(duration*fs)

    freqs = np.arange(npts/2 + 1)/(float(npts)/fs)

    pass_band = np.zeros(npts/2 + 1)
    pass_band[:len(pass_band)/2] = 1

    ir = tools.impulse_response(fs, pass_band, freqs, [freqs[0], freqs[-1]], filter_len=2**14, db=False)

    width = 0.05 # the width of the window used in impulse_response
    # Check the gain at a few samples where we know it should be approximately 0 or 1.
    freq_samples = np.array([width, 0.25, 0.5-width/2, 0.5+width/2, 0.75, 1.0-width])
    freqs, response = signal.freqz(ir, worN=np.pi*freq_samples)
    assert_array_almost_equal(np.abs(response),
                                [1.0, 1.0, 1.0, 0.0, 0.0, 0.0], decimal=5)

def test_impulse_db():
    fs = 5e5
    duration = 0.2
    npts = int(duration*fs)

    freqs = np.arange(npts/2 + 1)/(float(npts)/fs)

    pass_band = np.zeros(npts/2 + 1)
    pass_band[len(pass_band)/2:] = 20

    ir = tools.impulse_response(fs, pass_band, freqs, [freqs[0], freqs[-1]], filter_len=2**14, db=True)

    # w, h = signal.freqz(ir)
    # plt.plot(w, abs(h))
    # plt.show()

    width = 0.05 # the width of the window used in impulse_response
    # Check the gain at a few samples where we know it should be approximately 0 or 1.
    freq_samples = np.array([0.0, 0.25, 0.5-width/2, 0.5+width/2, 0.75, 1.0-width])
    freqs, response = signal.freqz(ir, worN=np.pi*freq_samples)
    assert_array_almost_equal(np.abs(response),
                                [1.0, 1.0, 1.0, 10.0, 10.0, 10.0], decimal=5)

def test_convolve_real_simple():
    # make sure correct dimensions come out, answers borrowed from scipy tests
    x = np.array([1,2,3])
    assert_array_almost_equal(tools.convolve_filter(x,x), [4,10,12])

def test_convolve_complex_simple():
    x = np.array([1+1j,2+2j,3+3j])
    assert_array_almost_equal(tools.convolve_filter(x,x),
                              [0+8j, 0+20j, 0+24j])

def test_convolve_no_impulse():
    x = np.array([1,2,3])
    assert_array_equal(tools.convolve_filter(x,None), x)

def test_tukey():
    npts = 100
    win = tools.tukey(npts, 0.1)
    assert_almost_equal(win[0], 0)
    assert_almost_equal(win[-1], 0)
    assert_array_almost_equal(win[[10,50,90]], [1.,1.,1.])

def test_smooth_return_len():
    x = np.random.random((100,))

    smx = tools.smooth(x, window_len=10)
    assert smx.shape == x.shape

    smx = tools.smooth(x, window_len=9)
    assert smx.shape == x.shape

    x = np.random.random((99,))
    smx = tools.smooth(x, window_len=10)
    assert smx.shape == x.shape

    x = np.random.random((99,))
    smx = tools.smooth(x, window_len=9)
    assert smx.shape == x.shape

def test_smooth_flat():
    x = np.ones(100)
    x[::2] = -1
    smx = tools.smooth(x, window_len=4)
    assert_array_almost_equal(smx, np.zeros(100))

def test_smooth_window_too_small():
    x = np.ones(100)
    x[::2] = -1
    smx = tools.smooth(x, window_len=2)
    assert_array_almost_equal(smx, x)

@raises(ValueError)
def test_smooth_bad_window():
    x = np.random.random((100,))
    smx = tools.smooth(x, window_len=10, window='tukey')

@raises(ValueError)
def test_smooth_bad_dim():
    x = np.ones((10,10))
    smx = tools.smooth(x, window_len=5)

@raises(ValueError)
def test_smooth_bad_win_len():
    x = np.ones((9,))
    smx = tools.smooth(x, window_len=10)

def test_audioread_wav():
    fs, signal = tools.audioread(sample.samplewav())
    assert signal.shape == (29758,)
    assert fs == 375000

def test_audioread_call1():
    fs, signal = tools.audioread(sample.samplecall1())
    assert signal.shape == (29152,)
    assert fs == 333333

def test_audiorate_wav():
    fs = tools.audiorate(sample.samplewav())
    assert fs == 375000

def test_audiorate_call1():
    fs = tools.audiorate(sample.samplecall1())
    assert fs == 333333
