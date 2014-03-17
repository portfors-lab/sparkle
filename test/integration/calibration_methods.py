from spikeylab.io.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import WhiteNoise, PureTone, FMSweep

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

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

    cal_func = interp1d(calfqs, calvals)
    frange = f[f0:f1]
    H = cal_func(frange)
    # convert to voltage scalars
    H = 10**((H).astype(float)/20)
    Xadjusted = X.copy()
    Xadjusted[f0:f1] *= H

    signal_calibrated = np.fft.irfft(Xadjusted)
    return signal_calibrated

def vf_calibration(sig, resp):
    xh = resp
    xh = xh/np.amax(xh) # normalize
    XH = np.fft.rfft(xh)

    x = sig
    x = x/np.amax(x) # normalize
    X = np.fft.rfft(x)
    XHmag = np.sqrt(np.real(XH)**2 + np.imag(XH)**2)
    Xmag = np.sqrt(np.real(X)**2 + np.imag(X)**2)

    H = Xmag/XHmag
    return np.fft.irfft(X/H)

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
tone_frequencies = range(5000, 110000, 2000)
# tone_frequencies = [5000, 50000, 100000]
nreps = 5
refv = 0.1 # Volts
refdb = 100 # dB SPL
calf = 5000
dur = 0.2 #seconds (window and stim)
fs = 5e5

player = FinitePlayer()
player.set_aochan(u"PCI-6259/ao0")
player.set_aichan(u"PCI-6259/ai0")
player.set_aidur(dur)
player.set_aisr(fs)

tone = PureTone()
tone.setDuration(dur)
tone.setRisefall(0.003)
tone.setIntensity(refdb)

calpeaks = []
fftpeaks = []
print 'gathering calibration curve...'
npts = dur*fs
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

vfunc = np.vectorize(calc_db)
calcurve_db = vfunc(calpeaks, cal_peak) * -1
calcurve_db2 = vfunc(fftpeaks, cal_peak2) * -1

# test calibration ----------------------------------------
frange = [5000, 100000] # range to apply calibration to

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
    freqs = np.arange(npts/2+1)/(float(npts)/fs)
    ftp = spectrum[freqs == tf][0]
    mag = np.sqrt(np.real(ftp)**2 + np.imag(ftp)**2)
    testpeaks2.append(mag)
print

print 'test curves finished'
test_peak2 = testpeaks2[tone_frequencies.index(calf)]

testcurve_db2 = vfunc(testpeaks2, test_peak2) * -1

##################################
# white noise test
wn = WhiteNoise()
wn.setDuration(dur)
wn.setIntensity(refdb)
wn_signal = wn.signal(fs, 0, refdb, refv)

# control stim, witout calibration
print 'control noise...'

mean_control = record(wn_signal)

# tone calibrated noise vmax peak
print 'calibrating noise vmax...'

wn_signal_calibrated = apply_calibration(wn_signal, fs, frange, tone_frequencies, calcurve_db)
mean_tcal = record(wn_signal_calibrated)

print 'calibrating noise fft...'

wn_signal_calibrated2 = apply_calibration(wn_signal, fs, frange, tone_frequencies, calcurve_db2)
mean_tcal2 = record(wn_signal_calibrated2)

print 'calibrating vf noise...'

wn_signal_calibrated3 = vf_calibration(wn_signal, mean_control)
mean_vfcal = record(wn_signal_calibrated3)

print 'plotting results...'
plt.figure()
plt.subplot(111)
plt.plot(tone_frequencies, calcurve_db, label='vmax before')
plt.plot(tone_frequencies, calcurve_db2, label='fft before')
plt.title("Calibration curve (attenuation dB)")
plt.plot(tone_frequencies, testcurve_db, label='vmax after')
plt.plot(tone_frequencies, testcurve_db2, label='fft after')
plt.legend()

fig = plt.figure()
plt.subplot(151)
plt.title('original signal')
plt.specgram(wn_signal, NFFT=512, Fs=fs)
plt.subplot(152)
plt.title('control recording')
plt.specgram(mean_control, NFFT=512, Fs=fs)
plt.subplot(153)
plt.title('vmax tcal')
plt.specgram(mean_tcal, NFFT=512, Fs=fs)

plt.subplot(154)
plt.title('fft tcal')
plt.specgram(mean_tcal2, NFFT=512, Fs=fs)

plt.subplot(155)
plt.title('vf cal')
plt.specgram(mean_vfcal, NFFT=512, Fs=fs)

# normalize results
print 'calculating error...'

ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(wn_signal, mean_control, frange, 'noise control')
tcal_err, tcal_err_sr, tcal_mae = calc_error(wn_signal, mean_tcal, frange, 'noise vmax')
tcal_err2, tcal_err_sr2, tcal_mae2 = calc_error(wn_signal, mean_tcal2, frange, 'noise fft mag')
vfcal_err, vfcal_err_sr, vfcal_mae = calc_error(wn_signal, mean_vfcal, frange, 'noise VF')

print '='*50
print 'noise control NMSE              {:.4f}, {:.4f}, {:.4f}'.format(ctrl_err, ctrl_err_sr, ctrl_mae)
print 'noise calibrated NMSE vmax      {:.4f}, {:.4f}, {:.4f}'.format(tcal_err, tcal_err_sr, tcal_mae)
print 'noise calibrated NMSE fft peaks {:.4f}, {:.4f}, {:.4f}'.format(tcal_err2, tcal_err_sr2, tcal_mae2)
print 'noise calibrated NMSE vf        {:.4f}, {:.4f}, {:.4f}'.format(vfcal_err, vfcal_err_sr, vfcal_mae)
print '='*50

chirp = FMSweep()
chirp.setDuration(dur)
chirp.setIntensity(refdb)
chirp_signal = chirp.signal(fs, 0, refdb, refv)

# control stim, witout calibration
print 'control chirp...'

mean_control_chirp = record(chirp_signal)

# tone calibrated noise
print 'calibrating chirp...'

chirp_signal_calibrated = apply_calibration(chirp_signal, fs, frange, tone_frequencies, calcurve_db)
mean_tcal_chirp = record(chirp_signal_calibrated)

print 'fft peak calibrated chrip...'

chirp_signal_calibrated2 = apply_calibration(chirp_signal, fs, frange, tone_frequencies, calcurve_db2)
mean_tcal_chirp2 = record(chirp_signal_calibrated2)

print 'calibrating vf chirp...'

chirp_signal_calibrated3 = vf_calibration(chirp_signal, mean_control_chirp)
mean_vfcal_chirp = record(chirp_signal_calibrated3)

plt.figure()
plt.subplot(151)
plt.title('original signal')
plt.specgram(chirp_signal, NFFT=512, Fs=fs)
plt.subplot(152)
plt.title('control recording')
plt.specgram(mean_control_chirp, NFFT=512, Fs=fs)
plt.subplot(153)
plt.title('tcal vmax recording')
plt.specgram(mean_tcal_chirp, NFFT=512, Fs=fs)
plt.subplot(154)
plt.title('tcal fft recording')
plt.specgram(mean_tcal_chirp2, NFFT=512, Fs=fs)
plt.subplot(155)
plt.title('vf recording')
plt.specgram(mean_vfcal_chirp, NFFT=512, Fs=fs)

ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(chirp_signal, mean_control_chirp, frange, 'chirp control')
tcal_err, tcal_err_sr, tcal_mae = calc_error(chirp_signal, mean_tcal_chirp, frange, 'chirp vmax')
tcal_err2, tcal_err_sr2, tcal_mae2 = calc_error(chirp_signal, mean_tcal_chirp2, frange, 'chirp fft mag')
vfcal_err, vfcal_err_sr, vfcal_mae = calc_error(chirp_signal, mean_vfcal_chirp, frange, 'chirp VF')

print '='*50
print 'chirp control NMSE              {:.4f}, {:.4f}, {:.4f}'.format(ctrl_err, ctrl_err_sr, ctrl_mae)
print 'chirp calibrated NMSE vmax      {:.4f}, {:.4f}, {:.4f}'.format(tcal_err, tcal_err_sr, tcal_mae)
print 'chirp calibrated NMSE fft peaks {:.4f}, {:.4f}, {:.4f}'.format(tcal_err2, tcal_err_sr2, tcal_mae2)
print 'chirp calibrated NMSE vf        {:.4f}, {:.4f}, {:.4f}'.format(vfcal_err, vfcal_err_sr, vfcal_mae)
print '='*50            

plt.show()
