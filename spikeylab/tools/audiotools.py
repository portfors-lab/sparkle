from __future__ import division
import numpy as np
from scipy.integrate import simps, trapz
import scipy.io.wavfile as wv
from scipy.interpolate import interp1d
from matplotlib import mlab
from matplotlib import pyplot
from scipy.signal import hann, fftconvolve

from PyQt4.QtGui import QImage

VERBOSE = False

def calc_db(peak, cal_peak):
    u""" converts voltage difference into deicbels : 20*log10(peak/cal_peak)"""
    try:
        pbdB = 20 * np.log10(peak/cal_peak)
    except ZeroDivisionError:
        print u'attempted division by zero:'
        print u'peak {}, caldb {}, calpeak {}'.format(peak, caldb, cal_peak)
        pbdB = np.nan
    return pbdB

def calc_noise(fft_vector, ix1,ix2):
    fft_slice = fft_vector[ix1:ix2]
    area = trapz(fft_slice)
    return area

def calc_spectrum(signal,rate):
    #calculate complex fft

    # pad with zeros?
    #padded_signal = np.zeros(len(signal*2))
    #padded_signal[:len(signal)] = signal
    #signal = padded_signal
    npts = len(signal)
    mdpt = (npts+1) % 2
    freq = np.arange(npts/2+mdpt)/(npts/rate)
    #print('freq len ', len(freq))

    sp = np.fft.rfft(signal)/npts
    #print('sp len ', len(sp))
    return freq, abs(sp)

def get_fft_peak(spectrum, freq, atfrequency=None):
    # find the peak values for spectrum
    if atfrequency is None:
        maxidx = spectrum.argmax(axis=0)
        f = freq[maxidx]
        spec_peak = np.amax(spectrum)
    else:
        f = atfrequency
        spec_peak = spectrum[freq==f]
    return spec_peak, f

def make_tone(freq,db,dur,risefall,samplerate, caldb=100, calv=0.1):
    """
    Produce a pure tone signal 

    :param freq: Frequency of the tone to be produced (Hz)
    :type freq: int
    :param db: Intensity of the tone in dB SPL
    :type db: int
    :param dur: duration (seconds)
    :type dur: float
    :param risefall: linear rise fall of (seconds)
    :type risefall: float
    :param samplerate: generation frequency of tone (Hz)
    :type samplerate: int
    :param caldb: Reference intensity (dB SPL). Together with calv, provides a reference point for what intensity equals what output voltage level
    :type caldb: int
    :param calv: Reference voltage (V). Together with calv, provides a reference point for what intensity equals what output voltage level
    :type calv: float
    """
    npts = dur * samplerate
    try:
        amp = (10 ** ((db-caldb)/20)*calv)

        if VERBOSE:
            print("current dB: {}, attenuation: {}, current frequency: {} kHz, AO Amp: {:.6f}".format(db, atten, freq/1000, amp))
            print("cal dB: {}, V at cal dB: {}".format(caldb, calv))

        rf_npts = risefall * samplerate
        #print('amp {}, freq {}, npts {}, rf_npts {}'
        # .format(amp,freq,npts,rf_npts))
    
        tone = amp * np.sin((freq*dur) * np.linspace(0, 2*np.pi, npts))
                    
        if risefall > 0:
            rf_npts = risefall * samplerate
            wnd = hann(rf_npts*2) # cosine taper
            tone[:rf_npts] = tone[:rf_npts] * wnd[:rf_npts]
            tone[-rf_npts:] = tone[-rf_npts:] * wnd[rf_npts:]

        timevals = np.arange(npts)/samplerate

    except:
        print("WARNING: Unable to produce tone")
        tone = np.zeros(npts)
        timevals = np.arange(npts)/samplerate
        raise

    return tone, timevals


def spectrogram(source, nfft=512, overlap=90, window='hanning'):
    if isinstance(source, basestring):
        try:
            sr, wavdata = wv.read(source)
        except:
            print u"Problem reading wav file"
            raise
        wavdata = wavdata.astype(float)
    else:
        sr, wavdata = source
        
    # normalize
    if np.max(abs(wavdata)) != 0:
        wavdata = wavdata/np.max(abs(wavdata))
    duration = len(wavdata)/sr

    if window == 'hanning':
        winfnc = mlab.window_hanning
    elif window == 'hamming':
        winfnc = np.hamming(nfft)
    elif window == 'blackman':
        winfnc = np.blackman(nfft)
    elif window == 'bartlett':
        winfnc = np.bartlett(nfft)
    elif window == None or window == 'none':
        winfnc = mlab.window_none

    noverlap = int(nfft*(float(overlap)/100))

    Pxx, freqs, bins = mlab.specgram(wavdata, NFFT=nfft, Fs=sr, noverlap=noverlap,
                                     pad_to=nfft*2, window=winfnc, detrend=mlab.detrend_none,
                                     sides='default', scale_by_freq=True)

    # convert to db scale for display
    spec = 10. * np.log10(Pxx)
    
    # inf values prevent spec from drawing in pyqtgraph
    # ... so set to miniumum value in spec?
    # would be great to have spec in db SPL, and set any -inf to 0
    spec[np.isneginf(spec)] = np.nan
    spec[np.isnan(spec)] = np.nanmin(spec)

    return spec, freqs, bins, duration

def smooth(x, window_len=99, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    Based from Scipy Cookbook
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len < 3:
        return x
    if window_len % 2 == 0:
        window_len +=1

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman', 'kaiser']:
        raise ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    elif window == 'kaiser':
        w = np.kaiser(window_len,4)
    else:
        w = eval('np.'+window+'(window_len)')

    y = np.convolve(w/w.sum(),s,mode='valid')
    return y[window_len/2-1:len(y)-window_len/2]


def convolve_filter(signal, impulse_response):
    if impulse_response is not None:
        # print 'interpolated calibration'#, self.calibration_frequencies
        adjusted_signal = fftconvolve(signal, impulse_response)
        adjusted_signal = adjusted_signal[len(impulse_response)/2:len(adjusted_signal)-len(impulse_response)/2 + 1]
        return adjusted_signal
    else:
        return signal


def calc_impulse_response(db_boost_array, frequencies, frange, decimation_factor=12, truncation_factor=4):
    # calculate filter kernel from attenuation vector
    # treat attenuation vector as magnitude frequency response of system
    npts = len(db_boost_array)
    fs = (frequencies[1] - frequencies[0]) * (npts - 1) *2

    # could decimate without interpolating, but leaving in for flexibility
    calc_func = interp1d(frequencies, db_boost_array)
    # reduce the number of points in the frequency response by decimation_factor 
    # decimated_freq = np.arange((npts)//(decimation_factor))/(float(npts-1-decimation_factor+(decimation_factor%2))/decimation_factor)*fs/2
    decimated_freq = np.arange(np.ceil(npts/decimation_factor))/((npts-1)/(decimation_factor/2))*fs
    
    print '-'*30
    print 'desired npts', np.ceil(npts/decimation_factor)
    print 'decimated freq range', decimated_freq[0], decimated_freq[-1]
    print 'provieded range', frequencies[0], frequencies[-1]
    decimated_attenuations = calc_func(decimated_freq)
    f0 = (np.abs(decimated_freq-frange[0])).argmin()
    f1 = (np.abs(decimated_freq-frange[1])).argmin()
    decimated_attenuations[:f0] = 0
    decimated_attenuations[f1:] = 0
    decimated_attenuations[f0:f1] = decimated_attenuations[f0:f1]*tukey(len(decimated_attenuations[f0:f1]), 0.05)
    freq_response = 10**((decimated_attenuations).astype(float)/20)

    impulse_response = np.fft.irfft(freq_response)
    
    # rotate to create causal filter, and truncate
    impulse_response = np.roll(impulse_response, len(impulse_response)//2)

    impulse_response = impulse_response[(len(impulse_response)//2)-(len(impulse_response)//truncation_factor//2):(len(impulse_response)//2)+(len(impulse_response)//truncation_factor//2)]
    
    #should I also window the impulse response???

    return impulse_response

def calc_attenuation_curve(signal, resp, fs, calf, smooth_pts=99):
    """Calculate an attenuation roll-off curve, from a signal and its recording"""
    # remove dc offset
    resp = resp - np.mean(resp)

    y = resp
    x = signal

    # convert time signals to frequency domain
    Y = np.fft.rfft(y)
    X = np.fft.rfft(x)

    # take the magnitude of signals
    Ymag = np.sqrt(Y.real**2 + Y.imag**2) # equivalent to abs(Y)
    Xmag = np.sqrt(X.real**2 + X.imag**2)

    # convert to decibel scale
    YmagdB = 20 * np.log10(Ymag)
    XmagdB = 20 * np.log10(Xmag)

    # now we can substract to get attenuation curve
    diffdB = XmagdB - YmagdB

    # may want to smooth results here?
    diffdB = smooth(diffdB, smooth_pts)

    # frequencies present in calibration spectrum
    npts = len(y)
    fq = np.arange(npts/2+1)/(float(npts)/fs)

    # shift by the given calibration frequency to align attenutation
    # with reference point set by user
    diffdB -= diffdB[fq == calf]

    return diffdB

def bb_calibration(signal, resp, fs, frange):
    """Given original signal and recording, spits out a calibrated signal"""
    # remove dc offset from recorded response (synthesized orignal shouldn't have one)
    dc = np.mean(resp)
    resp = resp - dc

    npts = len(signal)
    f0 = np.ceil(frange[0]/(float(fs)/npts))
    f1 = np.floor(frange[1]/(float(fs)/npts))

    y = resp
    # y = y/np.amax(y) # normalize
    Y = np.fft.rfft(y)

    x = signal
    # x = x/np.amax(x) # normalize
    X = np.fft.rfft(x)

    H = Y/X

    # still issues warning because all of Y/X is executed to selected answers from
    # H = np.where(X.real!=0, Y/X, 1)
    # H[:f0].real = 1
    # H[f1:].real = 1
    # H = smooth(H)

    A = X / H

    return np.fft.irfft(A)


def multiply_frequencies(signal, fs, frange, calfqs, calvals):
    """Given a vector of dB attenuations, adjust signal by 
       multiplication in the frequency domain"""
    pad_factor = 1.2
    npts = len(signal)

    X = np.fft.rfft(signal,  n=int(len(signal)*pad_factor))

    f = np.arange(npts/2+1)/(float(npts)/fs)
    f0 = (np.abs(f-frange[0])).argmin()
    f1 = (np.abs(f-frange[1])).argmin()

    cal_func = interp1d(calfqs, calvals)
    frange = f[f0:f1]
    Hroi = cal_func(frange)
    H = np.zeros((npts/2+1,))
    H[f0:f1] = Hroi

    H = smooth(H)

    H = 10**((H).astype(float)/20)

    # Xadjusted = X.copy()
    # Xadjusted[f0:f1] *= H
    # Xadjusted = smooth(Xadjusted)

    Xadjusted = X*H

    signal_calibrated = np.fft.irfft(Xadjusted)
    return signal_calibrated[:len(signal)]


def tukey(winlen, alpha):
    taper = hann(winlen*alpha)
    rect = np.ones(winlen-len(taper) + 1)
    win = fftconvolve(taper, rect)
    win = win / np.amax(win)
    return win