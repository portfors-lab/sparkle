import sys, time
import numpy as np
import matplotlib.pyplot as plt

from QtWrapper import QtGui, QtCore

from neurosound.acq.players import FinitePlayer
from neurosound.stim.types.stimuli_classes import PureTone
from neurosound.tools.audiotools import calc_db, calc_spectrum, \
                            convolve_filter, multiply_frequencies, \
                            signal_amplitude, calc_summed_db, rms

class MyTableWidgetItem(QtGui.QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except:
            return super(MyTableWidgetItem, self).__lt__(other)

def calc_error(predicted, recorded, fs, frange, refdb, refv, title=None):
    npts = len(predicted)

    dc = np.mean(recorded)
    recorded = recorded - dc

    f = np.arange(npts/2+1)/(float(npts)/fs)
    f0 = (np.abs(f-frange[0])).argmin()
    f1 = (np.abs(f-frange[1])).argmin()

    # predicted = predicted/np.amax(predicted)
    # recorded = recorded/np.amax(recorded)

    predicted_spectrum = abs(np.fft.rfft(predicted)/npts)
    recorded_spectrum = abs(np.fft.rfft(recorded)/npts)

    # evaluate error only for calibrated region
    predicted_roi = predicted_spectrum[f0:f1]
    recorded_roi = recorded_spectrum[f0:f1]

    # convert into dB scale
    predicted_db = 20. * np.log10(predicted_roi/ refv) + refdb  
    # recorded_db = calc_db(recorded_roi,0)
    recorded_db = (20.*np.log10((recorded_roi/np.sqrt(2))/0.004)) + 94

    mse = (np.sum((recorded_db - predicted_db)**2))/len(predicted_db)
    mae = abs(np.mean(recorded_db - predicted_db))
    rmse = np.sqrt(mse)
    # nrmse = rmse/(np.mean(recorded_db))

    # plt.figure()
    # plt.suptitle('{} {:.4f}'.format(title, rmse))
    # plt.subplot(211)
    # plt.plot(f[f0:f1], predicted_db)
    # plt.title("predicted")
    # plt.subplot(212)
    # plt.title("recorded")
    # plt.plot(f[f0:f1], recorded_db)
    # plt.show()

    # nrmse = np.around(nrmse, 2)
    mse = np.around(mse,2)
    rmse = np.around(rmse,2)
    mae = np.around(mae,2)

    return mse, rmse, mae


def record(player, sig, fs, atten=0, nreps=16):
    reps = []
    player.set_stim(sig, fs, atten)
    player.start()
    # print 'stim shape', sig.shape, 'acq points', int(player.aitime*player.aisr)
    # print 'samplerates', player.aisr, fs
    for irep in range(nreps):
        response = player.run()
        reps.append(response)
        player.reset()

    player.stop()
    return np.mean(reps, axis=0)

def play_record(sig, fs):
    dur = float(len(sig))/fs
    player = FinitePlayer()
    player.set_aochan(u"PCI-6259/ao0")
    player.set_aichan(u"PCI-6259/ai0")
    player.set_aidur(dur)
    player.set_aisr(fs)

    nreps = 3
    reps = []
    player.set_stim(sig, fs, 0)
    player.start()
    # print 'stim shape', sig.shape, 'acq points', int(player.aitime*player.aisr)
    # print 'samplerates', player.aisr, fs
    for irep in range(nreps):
        response = player.run()
        reps.append(response)
        player.reset()

    player.stop()
    return np.mean(reps, axis=0)


def apply_calibration(sig, fs, frange, calibration):
    """Takes the given *calibration* and applies to to signal *sig*, 
    implicitly determining calibration method by type of *calibration*
    """
    if isinstance(calibration, tuple):
        calfqs, calvals = calibration
        return multiply_frequencies(sig, fs, frange, calfqs, calvals)
    elif calibration is not None:
        return convolve_filter(sig, calibration)
    else:
        # calibration is none, means use uncalibrated signal
        return sig

def run_tone_curve(frequencies, intensities, player, fs, duration, 
               refdb, refv, calibration, frange):
    """Runs a calibration tone curve, spits out arrays with a bunch
    of different methods to calculate the dB SPL:

    * dB SPL calculated from the peak value of the response spectrum
    * dB SPL calculated from the RMS value of the signal
    * dB SPL calculated from the peak value of the signal
    * dB SPL calculated from the summed values of the spectrum
    """
    tone = PureTone()
    tone.setRisefall(0.003)
    vfunc = np.vectorize(calc_db)

    player.set_aidur(duration)
    player.set_aisr(fs)
    tone.setDuration(duration)

    specpeaks = np.zeros((len(intensities), len(frequencies)))
    toneamps_rms = np.zeros((len(intensities), len(frequencies)))
    toneamps_peak = np.zeros((len(intensities), len(frequencies)))
    tone_summed_curve_db = np.zeros((len(intensities), len(frequencies)))

    for db_idx, ti in enumerate(intensities):
        tone.setIntensity(ti)
        for freq_idx, tf in enumerate(frequencies):
            sys.stdout.write('.') # print without spaces
            tone.setFrequency(tf)
            calibrated_tone = apply_calibration(tone.signal(fs, 0, refdb, refv), 
                                                fs, frange, calibration)
            mean_response = record(player, calibrated_tone, fs)
            freqs, spectrum = calc_spectrum(mean_response, fs)
            mag = spectrum[(np.abs(freqs-tf)).argmin()]
            specpeaks[db_idx, freq_idx] = mag
            toneamps_rms[db_idx, freq_idx] = rms(mean_response, fs)
            toneamps_peak[db_idx, freq_idx] = np.amax(mean_response)
            idx = np.where((freqs > 5000) & (freqs < 100000))
            tone_summed_curve_db[db_idx, freq_idx] = calc_summed_db(spectrum[idx])

    spec_peak_curve_db = vfunc(specpeaks)
    tone_amp_rms_curve_db = vfunc(toneamps_rms)
    tone_amp_peak_curve_db = vfunc(toneamps_peak)

    return spec_peak_curve_db, tone_amp_rms_curve_db, tone_amp_peak_curve_db, tone_summed_curve_db