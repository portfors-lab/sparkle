import sys
import time

import matplotlib.pyplot as plt
import numpy as np

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.acq.players import FinitePlayer
from sparkle.stim.types.stimuli_classes import PureTone
from sparkle.tools.audiotools import calc_db, calc_spectrum, calc_summed_db, \
    convolve_filter, multiply_frequencies, rms, signal_amplitude

MPHONESENS = 0.109
MPHONECALDB = 94

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
    recorded_db = (20.*np.log10((recorded_roi/np.sqrt(2))/MPHONESENS)) + MPHONECALDB

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


def record(player, sig, fs, atten=0, nreps=9):
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
    player.set_aifs(fs)

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

    * dB SPL calculated from signal_amplitude from audiotools
    * dB SPL calculated from the peak value of the response spectrum
    * dB SPL calculated from the RMS value of the signal
    * dB SPL calculated from the peak value of the signal
    * dB SPL calculated from the summed values of the spectrum
    """
    tone = PureTone()
    tone.setRisefall(0.003)
    vfunc = np.vectorize(calc_db)

    player.set_aidur(duration)
    player.set_aifs(fs)
    tone.setDuration(duration)

    # many different ways to determine overall intensity of signal
    specpeaks = np.zeros((len(intensities), len(frequencies)))
    toneamps_rms = np.zeros((len(intensities), len(frequencies)))
    toneamps_peak = np.zeros((len(intensities), len(frequencies)))
    tone_summed_curve_db = np.zeros((len(intensities), len(frequencies)))
    tone_signal_amp = np.zeros((len(intensities), len(frequencies)))

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
            tone_summed_curve_db[db_idx, freq_idx] = calc_summed_db(spectrum[idx], MPHONESENS, MPHONECALDB)
            tone_signal_amp[db_idx, freq_idx] = signal_amplitude(mean_response, fs)

    spec_peak_curve_db = vfunc(specpeaks, MPHONESENS, MPHONECALDB)
    tone_amp_rms_curve_db = vfunc(toneamps_rms, MPHONESENS, MPHONECALDB)
    tone_amp_peak_curve_db = vfunc(toneamps_peak, MPHONESENS, MPHONECALDB)
    tone_signal_amp_db = vfunc(tone_signal_amp, MPHONESENS, MPHONECALDB)

    return tone_signal_amp_db, spec_peak_curve_db, tone_amp_rms_curve_db, tone_amp_peak_curve_db, tone_summed_curve_db


def record_refdb(player, calf, refv, fs):
    """records a tone to determine the dB SPL for a given voltage amplitude"""
    dur = 0.2
    reftone = PureTone()
    reftone.setRisefall(0.003)
    reftone.setDuration(dur)
    tempdb = 70 # doesn't matter what we use here
    reftone.setIntensity(tempdb)
    reftone.setFrequency(calf)
    ref_db_signal = reftone.signal(fs, 0, tempdb, refv)
    player.set_aidur(dur)
    player.set_aifs(fs)
    ref_db_response = record(player, ref_db_signal, fs)
    refdb = calc_db(signal_amplitude(ref_db_response, fs), MPHONESENS, MPHONECALDB)
    print "REFDB", refdb
    return refdb