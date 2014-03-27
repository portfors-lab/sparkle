from spikeylab.io.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import WhiteNoise, PureTone, FMSweep

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import convolve, fftconvolve

TONE_CAL = False
NOISE_CAL = True

def smooth(x,window_len=99):
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
 
    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    # if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
    #     raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    # if window == 'flat': #moving average
    #     w=np.ones(window_len,'d')
    # else:
        # w=eval('np.'+window+'(window_len)')

    w = np.kaiser(window_len,4)
    y=np.convolve(w/w.sum(),s,mode='valid')
    return y[window_len/2:len(y)-window_len/2]

def calc_db(peak, calpeak):
    pbdB = 20 * np.log10(peak/calpeak)
    return pbdB

def calc_error(predicted, recorded, frange, title=None):
    npts = len(predicted)
    f = np.arange(npts/2+1)/(float(npts)/fs)
    f0 = (np.abs(f-frange[0])).argmin()
    f1 = (np.abs(f-frange[1])).argmin()

    # predicted = predicted/np.amax(predicted)
    # recorded = recorded/np.amax(recorded)

    predicted_spectrum = np.fft.rfft(predicted)
    recorded_spectrum = np.fft.rfft(recorded)

    predicted_roi = predicted_spectrum[f0:f1]
    recorded_roi = recorded_spectrum[f0:f1]

    # normalize for ROI
    predicted_roi = abs(predicted_roi/np.amax(predicted_roi))
    recorded_roi = abs(recorded_roi/np.amax(recorded_roi))

    mse = (np.sum((recorded_roi.real - predicted_roi.real)**2))/npts
    mae = abs(np.mean(recorded_roi.real - predicted_roi.real))
    mse2 = np.sqrt(mse)

    plt.figure()
    plt.suptitle('{} {:.4f}'.format(title, mse2))
    plt.subplot(211)
    plt.plot(f[f0:f1], predicted_roi.real)
    plt.title("predicted")
    plt.subplot(212)
    plt.title("recorded")
    plt.plot(f[f0:f1], recorded_roi.real)

    return mse, mse2, mae

def apply_calibration(sig, fs, frange, calfqs, calvals):
    X = np.fft.rfft(sig)

    npts = len(sig)
    f = np.arange(npts/2+1)/(float(npts)/fs)
    f0 = (np.abs(f-frange[0])).argmin()
    f1 = (np.abs(f-frange[1])).argmin()

    # plt.figure()
    # plt.plot(calfqs,calvals)
    # plt.title('cal apply inputs')

    cal_func = interp1d(calfqs, calvals)
    frange = f[f0:f1]
    Hroi = cal_func(frange)
    H = np.zeros((npts/2+1,))
    H[f0:f1] = Hroi
    # plt.figure()
    # plt.plot(f,H)
    # plt.title('H apply cal pre-smoothing')
    H = smooth(H)
    # plt.figure()
    # plt.plot(f,H)
    # plt.title('H apply cal')
    # plt.show()
    # convert to voltage scalars
    H = 10**((H).astype(float)/20)
    # Xadjusted = X.copy()
    # Xadjusted[f0:f1] *= H
    # Xadjusted = smooth(Xadjusted)
    Xadjusted = X*H

    signal_calibrated = np.fft.irfft(Xadjusted)
    return signal_calibrated

def bb_cal_curve(sig, resp, fs, frange):
    """Given original signal and recording, generates a dB attenuation curve"""
    # remove dc offset from recorded response (orignal shouldn't have one)
    dc = np.mean(resp)
    resp = resp - dc

    npts = len(sig)
    f0 = np.ceil(frange[0]/(float(fs)/npts))
    f1 = np.floor(frange[1]/(float(fs)/npts))

    y = resp
    # y = y/np.amax(y) # normalize
    Y = np.fft.rfft(y)

    x = sig
    # x = x/np.amax(x) # normalize
    X = np.fft.rfft(x)
    
    # H = np.where(X.real!=0, Y/X, 1)
    # diffdB = 20 * np.log10(H)

    Ymag = np.sqrt(Y.real**2 + Y.imag**2)
    Xmag = np.sqrt(X.real**2 + X.imag**2)

    YmagdB = 20 * np.log10(Ymag)
    XmagdB = 20 * np.log10(Xmag)

    diffdB = YmagdB - XmagdB

    # restrict to desired frequencies and smooth
    # this should probably be done on the other side,
    # before it gets applied.
    # diffdB[:f0] = 0
    # diffdB[f1:] = 0
    diffdB = smooth(diffdB)
    diffdB = -1*diffdB

    fq = np.arange(npts/2+1)/(float(npts)/fs)

    return diffdB[f0:f1], fq[f0:f1]

def bb_calibration(sig, resp, fs, frange):
    """Given original signal and recording, spits out a calibrated signal"""
    # remove dc offset from recorded response (synthesized orignal shouldn't have one)
    dc = np.mean(resp)
    resp = resp - dc

    npts = len(sig)
    f0 = np.ceil(frange[0]/(float(fs)/npts))
    f1 = np.floor(frange[1]/(float(fs)/npts))

    y = resp
    # y = y/np.amax(y) # normalize
    Y = np.fft.rfft(y)

    x = sig
    # x = x/np.amax(x) # normalize
    X = np.fft.rfft(x)

    # can use magnitude too...
    """
    Ymag = np.sqrt(Y.real**2 + Y.imag**2)
    Xmag = np.sqrt(X.real**2 + X.imag**2)
    # zeros = Xmag == 0
    # Xmag[zeros] = 1
    # Hmag = Ymag/Xmag
    # Xmag[zeros] = 0
    Hmag = np.where(Xmag == 0, 0, Ymag/Xmag)
    Hmag[:f0] = 1
    Hmag[f1:] = 1
    # Hmag = smooth(Hmag)
    """

    H = Y/X

    # still issues warning because all of Y/X is executed to selected answers from
    # H = np.where(X.real!=0, Y/X, 1)
    H[:f0].real = 1
    H[f1:].real = 1
    H = smooth(H)

    A = X / H

    return np.fft.irfft(A)

def record(sig):
    reps = []
    player.set_stim(sig, fs)
    player.start()
    for irep in range(nreps):
        response = player.run()
        reps.append(response)
        player.reset()

    player.stop()
    return np.mean(reps, axis=0)

# method 1 Tone Curve
nreps = 5
refv = 0.1 # Volts
refdb = 100 # dB SPL
calf = 15000
dur = 0.2 #seconds (window and stim)
fs = 5e5
tone_frequencies = range(5000, 110000, 5000)
# tone_frequencies = [5000, 50000, 100000]
frange = [5000, 100000] # range to apply calibration to
npts = dur*fs

player = FinitePlayer()
player.set_aochan(u"PCI-6259/ao0")
player.set_aichan(u"PCI-6259/ai0")
player.set_aidur(dur)
player.set_aisr(fs)

tone = PureTone()
tone.setDuration(dur)
tone.setRisefall(0.003)
tone.setIntensity(refdb)

if not TONE_CAL and not NOISE_CAL:
    print 'Must choose at lease one calibration type'
    sys.exit()

vfunc = np.vectorize(calc_db)

if TONE_CAL:
    calpeaks = []
    fftpeaks = []
    print 'gathering calibration curve...'
    for tf in tone_frequencies:
        sys.stdout.write('.') # print without spaces
        reps = []
        tone.setFrequency(tf)
        tone_signal = tone.signal(fs, 0, refdb, refv)
        mean_response = record(tone_signal)
        vmax = np.sqrt(np.mean(pow(mean_response,2)))*1.414 #rms
        calpeaks.append(vmax)
        
        spectrum = np.fft.rfft(mean_response)
        freqs = np.arange(npts/2+1)/(float(npts)/fs)
        ftp = spectrum[freqs == tf][0]
        mag = np.sqrt(np.real(ftp)**2 + np.imag(ftp)**2)
        # print 'fft peak at', tf, mag

        fftpeaks.append(mag)
    print

    print 'calibration curve finished'
    cal_peak = calpeaks[tone_frequencies.index(calf)]
    cal_peak2 = fftpeaks[tone_frequencies.index(calf)]

    calcurve_db = vfunc(calpeaks, cal_peak) * -1
    calcurve_db2 = vfunc(fftpeaks, cal_peak2) * -1

    # test calibration ----------------------------------------

    # tone curve test
    testpeaks = []
    print 'testing calibration curve vmax...'
    for tf in tone_frequencies:
        sys.stdout.write('.') # print without spaces
        reps = []
        tone.setFrequency(tf)
        calibrated_tone = apply_calibration(tone.signal(fs, 0, refdb, refv), 
                                fs, frange, tone_frequencies, calcurve_db)

        mean_response = record(calibrated_tone)
        vmax = np.sqrt(np.mean(pow(mean_response,2)))*1.414 #rms
        testpeaks.append(vmax)
    print
    test_peak = testpeaks[tone_frequencies.index(calf)]

    testcurve_db = vfunc(testpeaks, test_peak) * -1
    freqs = np.arange(npts/2+1)/(float(npts)/fs)

    testpeaks2 = []
    print 'testing calibration curve fft peak...'
    for tf in tone_frequencies:
        sys.stdout.write('.') # print without spaces
        reps = []
        tone.setFrequency(tf)
        calibrated_tone = apply_calibration(tone.signal(fs, 0, refdb, refv), 
                                fs, frange, tone_frequencies, calcurve_db2)
        mean_response = record(calibrated_tone)
        spectrum = np.fft.rfft(mean_response)
        ftp = spectrum[freqs == tf][0]
        mag = np.sqrt(np.real(ftp)**2 + np.imag(ftp)**2)
        testpeaks2.append(mag)
    print

    print 'test curves finished'
    test_peak2 = testpeaks2[tone_frequencies.index(calf)]

    testcurve_db2 = vfunc(testpeaks2, test_peak2) * -1

    print 'plotting results...'
    plt.figure()
    plt.subplot(111)
    plt.plot(tone_frequencies, calcurve_db, label='vmax before')
    plt.plot(tone_frequencies, calcurve_db2, label='fft before')
    plt.title("Calibration curve (attenuation dB)")
    plt.plot(tone_frequencies, testcurve_db, label='vmax after')
    plt.plot(tone_frequencies, testcurve_db2, label='fft after')
    plt.legend()

##################################
# white noise test
wn = WhiteNoise()
wn.setDuration(dur)
wn.setIntensity(refdb)
wn_signal = wn.signal(fs, 0, refdb, refv)

# control stim, witout calibration
print 'control noise...'

mean_control_noise = record(wn_signal)

chirp = FMSweep()
chirp.setDuration(dur)
chirp.setIntensity(refdb)
chirp_signal = chirp.signal(fs, 0, refdb, refv)

# control stim, witout calibration
print 'control chirp...'

mean_control_chirp = record(chirp_signal)

if NOISE_CAL:
    # adjusted tuning curves from noise and chirp calibration procedure
    noise_curve_db, noise_frequencies = bb_cal_curve(wn_signal, mean_control_noise, fs, frange)
    # adjust according to calf
    calf_idx = int(frange[0]/(float(fs)/npts))
    noise_curve_db -= noise_curve_db[calf_idx]
    chirp_curve_db, chirp_frequencies = bb_cal_curve(chirp_signal, mean_control_chirp, fs, frange)
    chirp_curve_db -= chirp_curve_db[calf_idx]

    freqs = np.arange(npts/2+1)/(float(npts)/fs)
    testpeaks3 = []
    print 'testing calibration curve noise...'
    for tf in tone_frequencies:
        sys.stdout.write('.') # print without spaces
        reps = []
        tone.setFrequency(tf)
        calibrated_tone = apply_calibration(tone.signal(fs, 0, refdb, refv), 
                                fs, frange, noise_frequencies, noise_curve_db)
        mean_response = record(calibrated_tone)
        spectrum = np.fft.rfft(mean_response)
        ftp = spectrum[freqs == tf][0]
        mag = np.sqrt(np.real(ftp)**2 + np.imag(ftp)**2)
        testpeaks3.append(mag)
    print

    print 'test curves finished'
    test_peak3 = testpeaks3[tone_frequencies.index(calf)]
    testcurve_db3 = vfunc(testpeaks3, test_peak3) * -1

    testpeaks4 = []
    print 'testing calibration curve chirp...'
    for tf in tone_frequencies:
        sys.stdout.write('.') # print without spaces
        reps = []
        tone.setFrequency(tf)
        calibrated_tone = apply_calibration(tone.signal(fs, 0, refdb, refv), 
                                fs, frange, chirp_frequencies, chirp_curve_db)
        mean_response = record(calibrated_tone)
        spectrum = np.fft.rfft(mean_response)
        ftp = spectrum[freqs == tf][0]
        mag = np.sqrt(np.real(ftp)**2 + np.imag(ftp)**2)
        testpeaks4.append(mag)
    print

    print 'test curves finished'
    test_peak4 = testpeaks4[tone_frequencies.index(calf)]
    testcurve_db4 = vfunc(testpeaks4, test_peak4) * -1

    plt.plot(noise_frequencies, noise_curve_db, label='noise before')
    plt.plot(chirp_frequencies, chirp_curve_db, label='chirp before')
    plt.plot(tone_frequencies, testcurve_db3, label='noise after')
    plt.plot(tone_frequencies, testcurve_db4, label='chirp after')
    plt.legend()

if TONE_CAL:
    # tone calibrated noise vmax peak
    print 'calibrating noise vmax...'

    wn_signal_calibrated = apply_calibration(wn_signal, fs, frange, tone_frequencies, calcurve_db)
    mean_tcal = record(wn_signal_calibrated)

    print 'calibrating noise fft...'

    wn_signal_calibrated2 = apply_calibration(wn_signal, fs, frange, tone_frequencies, calcurve_db2)
    mean_tcal2 = record(wn_signal_calibrated2)

if NOISE_CAL:
    print 'calibrating vf noise...'

    # wn_signal_calibrated3 = bb_calibration(wn_signal, mean_control_noise, fs, frange)
    wn_signal_calibrated3 = apply_calibration(wn_signal, fs, frange, noise_frequencies, noise_curve_db)
    mean_vfcal = record(wn_signal_calibrated3)


# Report results ------------------
nsubplots = 2
if TONE_CAL:
    nsubplots += 2
if NOISE_CAL:
    nsubplots += 1

fig = plt.figure()
plt.subplot(1, nsubplots, 1)
plt.title('original signal')
plt.specgram(wn_signal, NFFT=512, Fs=fs)
plt.subplot(1, nsubplots, 2)
plt.title('control recording')
plt.specgram(mean_control_noise, NFFT=512, Fs=fs)

iplot = 3
if TONE_CAL:
    plt.subplot(1, nsubplots, iplot)
    plt.title('vmax tcal')
    plt.specgram(mean_tcal, NFFT=512, Fs=fs)
    iplot += 1
    plt.subplot(1, nsubplots, iplot)
    plt.title('fft tcal')
    plt.specgram(mean_tcal2, NFFT=512, Fs=fs)
    iplot += 1
if NOISE_CAL:
    plt.subplot(1, nsubplots, iplot)
    plt.title('vf cal')
    plt.specgram(mean_vfcal, NFFT=512, Fs=fs)

ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(wn_signal, mean_control_noise, frange, 'noise control')
print '='*50
print 'noise control NMSE              {:.4f}, {:.4f}, {:.4f}'.format(ctrl_err, ctrl_err_sr, ctrl_mae)
if TONE_CAL:
    tcal_err, tcal_err_sr, tcal_mae = calc_error(wn_signal, mean_tcal, frange, 'noise vmax')
    tcal_err2, tcal_err_sr2, tcal_mae2 = calc_error(wn_signal, mean_tcal2, frange, 'noise fft mag')
    print 'noise calibrated NMSE vmax      {:.4f}, {:.4f}, {:.4f}'.format(tcal_err, tcal_err_sr, tcal_mae)
    print 'noise calibrated NMSE fft peaks {:.4f}, {:.4f}, {:.4f}'.format(tcal_err2, tcal_err_sr2, tcal_mae2)
if NOISE_CAL:
    vfcal_err, vfcal_err_sr, vfcal_mae = calc_error(wn_signal, mean_vfcal, frange, 'noise VF')
    print 'noise calibrated NMSE vf        {:.4f}, {:.4f}, {:.4f}'.format(vfcal_err, vfcal_err_sr, vfcal_mae)    
print '='*50



if TONE_CAL:
    # tone calibrated noise
    print 'calibrating chirp...'

    chirp_signal_calibrated = apply_calibration(chirp_signal, fs, frange, tone_frequencies, calcurve_db)
    mean_tcal_chirp = record(chirp_signal_calibrated)

    print 'fft peak calibrated chrip...'

    chirp_signal_calibrated2 = apply_calibration(chirp_signal, fs, frange, tone_frequencies, calcurve_db2)
    mean_tcal_chirp2 = record(chirp_signal_calibrated2)

if NOISE_CAL:
    print 'calibrating vf chirp...'

    # chirp_signal_calibrated3 = bb_calibration(chirp_signal, mean_control_chirp, fs, frange)
    chirp_signal_calibrated3 = apply_calibration(chirp_signal, fs, frange, chirp_frequencies, chirp_curve_db)
    mean_vfcal_chirp = record(chirp_signal_calibrated3)

# plt.figure()
# plt.specgram(chirp_signal_calibrated2, NFFT=512, Fs=fs)
# plt.title('fft peak cal signal')
plt.figure()
plt.title('vf cal signal')
plt.specgram(chirp_signal_calibrated3, NFFT=512, Fs=fs)

plt.figure()
plt.subplot(1, nsubplots, 1)
plt.title('original signal')
plt.specgram(chirp_signal, NFFT=512, Fs=fs)
plt.subplot(1, nsubplots, 2)
plt.title('control recording')
plt.specgram(mean_control_chirp, NFFT=512, Fs=fs)

iplot = 3
if TONE_CAL:
    plt.subplot(1, nsubplots, iplot)
    plt.title('tcal vmax recording')
    plt.specgram(mean_tcal_chirp, NFFT=512, Fs=fs)
    iplot += 1
    plt.subplot(1, nsubplots, iplot)
    plt.title('tcal fft recording')
    plt.specgram(mean_tcal_chirp2, NFFT=512, Fs=fs)
    iplot += 1
if NOISE_CAL:
    plt.subplot(1, nsubplots, iplot)
    plt.title('vf recording')
    plt.specgram(mean_vfcal_chirp, NFFT=512, Fs=fs)

ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(chirp_signal, mean_control_chirp, frange, 'chirp control')
print '='*50
print 'chirp control NMSE              {:.4f}, {:.4f}, {:.4f}'.format(ctrl_err, ctrl_err_sr, ctrl_mae)
if TONE_CAL:
    tcal_err, tcal_err_sr, tcal_mae = calc_error(chirp_signal, mean_tcal_chirp, frange, 'chirp vmax')
    tcal_err2, tcal_err_sr2, tcal_mae2 = calc_error(chirp_signal, mean_tcal_chirp2, frange, 'chirp fft mag')
    print 'chirp calibrated NMSE vmax      {:.4f}, {:.4f}, {:.4f}'.format(tcal_err, tcal_err_sr, tcal_mae)
    print 'chirp calibrated NMSE fft peaks {:.4f}, {:.4f}, {:.4f}'.format(tcal_err2, tcal_err_sr2, tcal_mae2)
if NOISE_CAL:
    vfcal_err, vfcal_err_sr, vfcal_mae = calc_error(chirp_signal, mean_vfcal_chirp, frange, 'chirp VF')
    print 'chirp calibrated NMSE vf        {:.4f}, {:.4f}, {:.4f}'.format(vfcal_err, vfcal_err_sr, vfcal_mae)
print '='*50            

plt.show()
