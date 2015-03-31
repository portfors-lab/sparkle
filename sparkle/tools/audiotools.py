from __future__ import division

import os
import wave

import numpy as np
import scipy.io.wavfile as wv
import yaml
from matplotlib import mlab
from scipy.interpolate import interp1d
from scipy.signal import fftconvolve, hann

VERBOSE = False

with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),'settings.conf'), 'r') as yf:
    config = yaml.load(yf)
USE_RMS = config['use_rms']

def calc_db(peak, refval, mphonecaldb=0):
    u""" 
    Converts voltage difference into decibels : 20*log10(peak/refval)
    
    :param peak: amplitude
    :type peak: float or np.array
    :param refval: This can be either a another sound peak(or RMS val), to get the dB difference, or the microphone mphone_sensitivity
    :type refval: float
    :param mphonecaldb: If using the microphone sensitivity for refval, provide the dB SPL the microphone was calibrated at. Otherwise, leave as 0
    :type mphonecaldb: int
    :returns: float -- decibels difference (comparision), or dB SPL (using microphone sensitivity)
    """
    if refval == 0:
        return np.nan
    if hasattr(peak, '__iter__'):
        peak[peak == 0] = np.nan
    pbdB = mphonecaldb + (20.*np.log10(peak/refval))
    return pbdB

def calc_summed_db(spectrum, mphonesens, mphonecaldb=0):
    x = sum(spectrum ** 2)
    pbdB = mphonecaldb + (10.*np.log10(x/(mphonesens**2)))
    return pbdB

def sum_db(x):
    power = x/10
    tmp = [10**i for i in power]
    s = 10.*np.log10(sum(tmp))    
    return s

def calc_spectrum(signal,rate):
    """Return the spectrum and frequency indexes for real-valued input signal"""
    npts = len(signal)
    padto = 1<<(npts-1).bit_length()
    # print 'length of signal {}, pad to {}'.format(npts, padto)
    npts = padto

    sp = np.fft.rfft(signal, n=padto)/npts
    #print('sp len ', len(sp))
    freq = np.arange((npts/2)+1)/(npts/rate)
    #print('freq len ', len(freq))
    return freq, abs(sp)

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
    :param calv: Reference voltage (V). Together with caldb, provides a reference point for what intensity equals what output voltage level
    :type calv: float
    :returns: tone, timevals -- the signal and the time index values
    """
    if risefall > dur:
        raise ValueError('Duration must be greater than risefall time')
    if samplerate <= 0:
        raise ValueError("Samplerate must be greater than 0")
    if caldb <= 0:
        raise ValueError("Calibration dB SPL must be greater than 0")

    npts = int(dur * samplerate)
    amp = (10 ** ((db-caldb)/20)*calv)
    if USE_RMS:
        amp = amp*1.414213562373

    if VERBOSE:
        print("current dB: {}, fs: {}, current frequency: {} kHz, AO Amp: {:.6f}".format(db, samplerate, freq/1000, amp))
        print("cal dB: {}, V at cal dB: {}".format(caldb, calv))

    tone = amp * np.sin((freq*dur) * np.linspace(0, 2*np.pi, npts))
              
    # print 'tone max', np.amax(tone)  
    if risefall > 0:
        rf_npts = int(risefall * samplerate) // 2
        # print('amp {}, freq {}, npts {}, rf_npts {}'.format(amp,freq,npts,rf_npts))
        wnd = hann(rf_npts*2) # cosine taper
        tone[:rf_npts] = tone[:rf_npts] * wnd[:rf_npts]
        tone[-rf_npts:] = tone[-rf_npts:] * wnd[rf_npts:]

    timevals = np.arange(npts)/samplerate

    return tone, timevals


def spectrogram(source, nfft=512, overlap=90, window='hanning', caldb=93, calv=2.83):
    """
    Produce a matrix of spectral intensity, uses matplotlib's specgram
    function. Output is in dB scale.

    :param source: filename of audiofile, or samplerate and vector of audio signal
    :type source: str or (int, numpy.ndarray)
    :param nfft: size of nfft window to use
    :type nfft: int
    :param overlap: percent overlap of window
    :type overlap: number
    :param window: Type of window to use, choices are hanning, hamming, blackman, bartlett or none (rectangular)
    :type window: string
    :returns: spec -- 2D array of intensities, freqs -- yaxis labels, bins -- time bin labels, duration -- duration of signal
    """
    if isinstance(source, basestring):
        fs, wavdata = audioread(source)
    else:
        fs, wavdata = source
        
    #truncate to nears ms
    duration = float(len(wavdata))/fs
    desired_npts = int((np.trunc(duration*1000)/1000)*fs)
    # print 'LENGTH {}, DESIRED {}'.format(len(wavdata), desired_npts)
    wavdata = wavdata[:desired_npts]
    duration = len(wavdata)/fs

    if VERBOSE:
        amp = rms(wavdata, fs)
        print 'RMS of input signal to spectrogram', amp

    # normalize
    if len(wavdata) > 0 and np.max(abs(wavdata)) != 0:
        wavdata = wavdata/np.max(abs(wavdata))

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

    Pxx, freqs, bins = mlab.specgram(wavdata, NFFT=nfft, Fs=fs, noverlap=noverlap,
                                     pad_to=nfft*2, window=winfnc, detrend=mlab.detrend_none,
                                     sides='default', scale_by_freq=False)

    # log of zero is -inf, which is not great for plotting
    Pxx[Pxx == 0] = np.nan

    # convert to db scale for display
    spec = 20. * np.log10(Pxx)
    
    # set 0 to miniumum value in spec?
    # would be great to have spec in db SPL, and set any -inf to 0
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
    """
    Convovle the two input signals, if impulse_response is None,
    returns the unaltered signal
    """
    if impulse_response is not None:
        # print 'interpolated calibration'#, self.calibration_frequencies
        adjusted_signal = fftconvolve(signal, impulse_response)
        adjusted_signal = adjusted_signal[len(impulse_response)/2:len(adjusted_signal)-len(impulse_response)/2 + 1]
        return adjusted_signal
    else:
        return signal


def impulse_response(genrate, fresponse, frequencies, frange, filter_len=2**14, db=True):
    """
    Calculate filter kernel from attenuation vector.
    Attenuation vector should represent magnitude frequency response of system
    
    :param genrate: The generation samplerate at which the test signal was played
    :type genrate: int
    :param fresponse: Frequency response of the system in dB, i.e. relative attenuations of frequencies
    :type fresponse: numpy.ndarray
    :param frequencies: corresponding frequencies for the fresponse
    :type frequencies: numpy.ndarray
    :param frange: the min and max frequencies for which the filter kernel will affect
    :type frange: (int, int)
    :param filter_len: the desired length for the resultant impulse response
    :type filter_len: int
    :param db: whether the fresponse given is the a vector of multiplication or decibel factors
    :type db: bool
    :returns: numpy.ndarray -- the impulse response
    """

    freq = frequencies
    max_freq = genrate/2+1

    attenuations = np.zeros_like(fresponse)
    # add extra points for windowing
    winsz = 0.05 # percent
    lowf = max(0, frange[0] - (frange[1] - frange[0])*winsz)
    highf = min(frequencies[-1], frange[1] + (frange[1] - frange[0])*winsz)

    f0 = (np.abs(freq-lowf)).argmin()
    f1 = (np.abs(freq-highf)).argmin()
    fmax = (np.abs(freq-max_freq)).argmin() + 1
    attenuations[f0:f1] = fresponse[f0:f1]*tukey(len(fresponse[f0:f1]), winsz)
    if db:
        freq_response = 10**((attenuations).astype(float)/20)
    else:
        freq_response = attenuations

    freq_response = freq_response[:fmax]

    impulse_response = np.fft.irfft(freq_response)
    
    # rotate to create causal filter, and truncate
    impulse_response = np.roll(impulse_response, len(impulse_response)//2)

    # truncate
    if filter_len < len(impulse_response):
        startidx = (len(impulse_response)//2)-(filter_len//2)
        stopidx = (len(impulse_response)//2)+(filter_len//2)
        impulse_response = impulse_response[startidx:stopidx]
    
    # should I also window the impulse response - by how much?
    impulse_response = impulse_response * tukey(len(impulse_response), 0.05)

    return impulse_response

def attenuation_curve(signal, resp, fs, calf, smooth_pts=99):
    """
    Calculate an attenuation roll-off curve, from a signal and its recording

    :param signal: ouput signal delivered to the generation hardware
    :type signal: numpy.ndarray    
    :param resp: recording of given signal, as recieved from microphone
    :type resp: numpy.ndarray
    :param fs: input and output samplerate (should be the same)
    :type fs: int
    :param smooth_pts: amount of averaging to use on the result
    :type smooth_pts: int
    :returns: numpy.ndarray -- attenuation vector
    """
    # remove dc offset
    y = resp - np.mean(resp)
    x = signal

    # frequencies present in calibration spectrum
    npts = len(y)
    fq = np.arange(npts/2+1)/(float(npts)/fs)

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

    # shift by the given calibration frequency to align attenutation
    # with reference point set by user
    fidx = (np.abs(fq-calf)).argmin()
    diffdB -= diffdB[fidx]

    return diffdB

def calibrate_signal(signal, resp, fs, frange):
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


def multiply_frequencies(signal, fs, frange, calibration_frequencies, attendB):
    """Given a vector of dB attenuations, adjust signal by 
       multiplication in the frequency domain"""
    npts = len(signal)
    padto = 1<<(npts-1).bit_length()

    X = np.fft.rfft(signal, n=padto)

    npts = padto
    f = np.arange((npts/2)+1)/(npts/fs)
    
    fidx_low = (np.abs(f-frange[0])).argmin()
    fidx_high = (np.abs(f-frange[1])).argmin()

    cal_func = interp1d(calibration_frequencies, attendB)
    roi = f[fidx_low:fidx_high]
    Hroi = cal_func(roi)
    H = np.zeros((len(X),))
    H[fidx_low:fidx_high] = Hroi

    H = smooth(H)
    # print 'H dB max', np.amax(H)

    H = 10**((H).astype(float)/20)
    # print 'H amp max', np.amax(H)

    # Xadjusted = X.copy()
    # Xadjusted[fidx_low:fidx_high] *= H
    # Xadjusted = smooth(Xadjusted)

    Xadjusted = X*H
    # print 'X max', np.amax(abs(X))
    # print 'Xadjusted max', np.amax(abs(Xadjusted))

    signal_calibrated = np.fft.irfft(Xadjusted)
    return signal_calibrated[:len(signal)]


def tukey(winlen, alpha):
    """
    Generate a tukey (tapered cosine) window
    :param winlen: length of the window, in samples
    :type winlen: int
    :param alpha: proportion of the window to be tapered. 
    0 = rectangular window
    1.0 = hann window
    :type alpha: float
    """
    taper = hann(winlen*alpha)
    rect = np.ones(winlen-len(taper) + 1)
    win = fftconvolve(taper, rect)
    win = win / np.amax(win)
    return win

def audioread(filename):
    """Reads an audio signal from file.

    Supported formats : wav

    :param filename: filename of the audiofile to load
    :type filename: str
    :returns: int, numpy.ndarray -- samplerate, array containing the audio signal
    """
    try:
        if '.wav' in filename.lower():
            fs, signal = wv.read(filename)
        elif '.call' in filename.lower():
            with open(filename, 'rb') as f:
                signal = np.fromfile(f, dtype=np.int16)
            fs = 333333
        else:
            raise IOError("Unsupported audio format for file: {}".format(filename))
    except:
        print u"Problem reading wav file"
        raise
    signal = signal.astype(float)
    return fs, signal 

def audiorate(filename):
    """Determines the samplerate of the given audio recording file

    :param filename: filename of the audiofile
    :type filename: str
    :returns: int -- samplerate of the recording
    """
    if '.wav' in filename.lower():
        wf =  wave.open(filename)
        fs= wf.getframerate()
        wf.close()
    elif '.call' in filename.lower():
        fs = 333333
    else:
        raise IOError("Unsupported audio format for file: {}".format(filename))

    return fs

def rms(signal, fs):
    """Returns the root mean square (RMS) of the given *signal*

    :param signal: a vector of electric potential
    :type signal: numpy.ndarray
    :param fs: samplerate of the signal (Hz)
    :type fs: int
    :returns: float -- the RMS value of the signal
    """
    # if a signal contains a some silence, taking the RMS of the whole
    # signal will be calculated as less loud as a signal without a silent
    # period. I don't like this, so I am going to chunk the signals, and
    # take the value of the most intense chunk
    chunk_time = 0.001 # 1 ms chunk
    chunk_samps = int(chunk_time*fs)
    amps = []
    if chunk_samps > 10:
        for i in range(0, len(signal)-chunk_samps, chunk_samps):
            amps.append(np.sqrt(np.mean(pow(signal[i:i+chunk_samps],2))))
        amps.append(np.sqrt(np.mean(pow(signal[len(signal)-chunk_samps:],2))))
        return np.amax(amps)
    else:
        # samplerate low, just rms the whole thing
        return np.sqrt(np.mean(pow(signal,2)))

def signal_amplitude(signal, fs):
    if USE_RMS:
        amp = rms(signal, fs)
    else:
        amp = np.amax(abs(signal))
    return amp
