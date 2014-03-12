from spikeylab.io.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import WhiteNoise, PureTone, FMSweep

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def calc_db(peak, calpeak):
    pbdB = 20 * np.log10(peak/calpeak)
    return pbdB

def calc_error(predicted, recorded, frange):
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
    predicted_roi = predicted_roi/np.amax(predicted_roi)
    recorded_roi = recorded_roi/np.amax(recorded_roi)

    plt.figure()
    plt.subplot(211)
    plt.plot(f[f0:f1], predicted_roi.real)
    plt.title("predicted")
    plt.subplot(212)
    plt.title("recorded")
    plt.plot(f[f0:f1], recorded_roi.real)

    mse = (np.sum(recorded_roi.real - predicted_roi.real)**2)/npts
    mae = abs(np.mean(recorded_roi.real - predicted_roi.real))
    return mse, np.sqrt(mse), mae

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
print 'gathering calibration curve...'
for tf in tone_frequencies:
    sys.stdout.write('.') # print without spaces
    reps = []
    tone.setFrequency(tf)
    player.set_stim(tone.signal(fs, 0, refdb, refv), fs)
    player.start()
    for irep in range(nreps):
        response = player.run()
        reps.append(response)
        player.reset()
    player.stop()
    mean_response = np.mean(reps, axis=0)
    vmax = np.sqrt(np.mean(pow(response,2)))*1.414 #rms
    calpeaks.append(vmax)
print

print 'calibration curve finished'
cal_peak = calpeaks[tone_frequencies.index(calf)]

vfunc = np.vectorize(calc_db)
calcurve_db = vfunc(calpeaks, cal_peak) * -1

# test calibration ----------------------------------------
frange = [5000, 100000] # range to apply calibration to

# tone curve test
testpeaks = []
print 'testing calibration curve...'
for tf in tone_frequencies:
    sys.stdout.write('.') # print without spaces
    reps = []
    tone.setFrequency(tf)
    calibrated_tone = apply_calibration(tone.signal(fs, 0, refdb, refv), 
                            fs, frange, tone_frequencies, calcurve_db)
    player.set_stim(calibrated_tone, fs)
    player.start()
    for irep in range(nreps):
        response = player.run()
        reps.append(response)
        player.reset()
    player.stop()
    mean_response = np.mean(reps, axis=0)
    vmax = np.sqrt(np.mean(pow(response,2)))*1.414 #rms
    testpeaks.append(vmax)
print

print 'test curve finished'
cal_peak = testpeaks[tone_frequencies.index(calf)]

vfunc = np.vectorize(calc_db)
testcurve_db = vfunc(testpeaks, cal_peak) * -1

# white noise test
wn = WhiteNoise()
wn.setDuration(dur)
wn.setIntensity(refdb)
wn_signal = wn.signal(fs, 0, refdb, refv)

# control stim, witout calibration
print 'control noise...'
reps = []
player.set_stim(wn_signal, fs)
player.start()
for irep in range(nreps):
    response = player.run()
    reps.append(response)
    player.reset()

player.stop()
mean_control = np.mean(reps, axis=0)

# tone calibrated noise
print 'calibrating noise...'

wn_signal_calibrated = apply_calibration(wn_signal, fs, frange, tone_frequencies, calcurve_db)

reps = []
player.set_stim(wn_signal_calibrated, fs)
player.start()
for irep in range(nreps):
    response = player.run()
    reps.append(response)
    player.reset()

player.stop()
mean_tcal = np.mean(reps, axis=0)

print 'plotting results...'
plt.figure()
plt.subplot(111)
p0 = plt.plot(tone_frequencies, calcurve_db)
plt.title("Calibration curve (attenuation dB)")
p1 = plt.plot(tone_frequencies, testcurve_db)
# plt.legend([p0, p1], ['original', 'calibrated'])

plt.figure()
plt.subplot(131)
plt.title('original signal')
plt.specgram(wn_signal, NFFT=512, Fs=fs)
plt.subplot(132)
plt.title('control recording')
plt.specgram(mean_control, NFFT=512, Fs=fs)
plt.subplot(133)
plt.title('calibrated recording')
plt.specgram(mean_tcal, NFFT=512, Fs=fs)

# normalize results
print 'calculating error...'

ctrl_error, ctrl_error2, mae1 = calc_error(wn_signal, mean_control, frange)
tcal_error, tcal_error2, mae2 = calc_error(wn_signal, mean_tcal, frange)

print '='*40
print 'noise control NMSE', ctrl_error, ctrl_error2, mae1
print 'noise calibrated NMSE', tcal_error, tcal_error2, mae2

chirp = FMSweep()
chirp.setDuration(dur)
chirp.setIntensity(refdb)
chirp_signal = chirp.signal(fs, 0, refdb, refv)

# control stim, witout calibration
print 'control chirp...'
reps = []
player.set_stim(chirp_signal, fs)
player.start()
for irep in range(nreps):
    response = player.run()
    reps.append(response)
    player.reset()

player.stop()
mean_control_chirp = np.mean(reps, axis=0)

# tone calibrated noise
print 'calibrating chirp...'

chirp_signal_calibrated = apply_calibration(chirp_signal, fs, frange, tone_frequencies, calcurve_db)

reps = []
player.set_stim(chirp_signal_calibrated, fs)
player.start()
for irep in range(nreps):
    response = player.run()
    reps.append(response)
    player.reset()

player.stop()
mean_tcal_chirp = np.mean(reps, axis=0)

plt.figure()
plt.subplot(131)
plt.title('original signal')
plt.specgram(chirp_signal, NFFT=512, Fs=fs)
plt.subplot(132)
plt.title('control recording')
plt.specgram(mean_control_chirp, NFFT=512, Fs=fs)
plt.subplot(133)
plt.title('calibrated recording')
plt.specgram(mean_tcal_chirp, NFFT=512, Fs=fs)

ctrl_error3, ctrl_error4, mae3 = calc_error(chirp_signal, mean_control_chirp, frange)
tcal_error3, tcal_error4,  mae4 = calc_error(chirp_signal, mean_tcal_chirp, frange)
print 'chirp control NMSE', ctrl_error3, ctrl_error4, mae3
print 'chirp calibrated NMSE', tcal_error3, tcal_error4, mae4

plt.show()
