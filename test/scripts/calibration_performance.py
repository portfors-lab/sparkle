from spikeylab.acq.players import FinitePlayer
from spikeylab.stim.stimulusmodel import StimulusModel
from spikeylab.stim.types.stimuli_classes import WhiteNoise, FMSweep
from spikeylab.tools.audiotools import tukey, impulse_response, \
                convolve_filter, attenuation_curve, multiply_frequencies
from test.scripts.util import calc_error, record, MyTableWidgetItem


import sys, time, os, json
import numpy as np

from PyQt4 import QtGui, QtCore

def apply_calibration(sig, fs, frange, calfqs, calvals, method):
    if method == 'multiply':
        return multiply_frequencies(sig, fs, frange, calfqs, calvals)
    elif method == 'convolve':
        return convolve_filter(sig, calvals)
    else:
        raise Exception("Unknown calibration method: {}".format(method))


MULT_CAL = True
CONV_CAL = True

SMOOTHING = 99
# TRUNCATIONS = [1, 2, 4, 8]
TRUNCATIONS = [1, 4, 12, 100]

# method 1 Tone Curve
nreps = 3
refv = 1.2 # Volts
refdb = 115 # dB SPL
calf = 15000
dur = 0.2 #seconds (window and stim)
fs = 5e5
nsignals = 200
frange = [2000, 105000] # range to apply calibration to

if __name__ == "__main__":
    npts = dur*fs

    player = FinitePlayer()
    player.set_aochan(u"PCI-6259/ao0")
    player.set_aichan(u"PCI-6259/ai0")
    player.set_aidur(dur)
    player.set_aisr(fs)

    if not CONV_CAL and not MULT_CAL:
        print 'Must choose at lease one calibration type'
        sys.exit()


    ##################################
    # white noise test
    wn = WhiteNoise()
    wn.setDuration(dur)
    wn.setIntensity(refdb)
    wn_signal = wn.signal(fs, 0, refdb, refv)

    # control stim, witout calibration
    print 'control noise...'

    mean_control_noise = record(player, wn_signal, fs)

    freqs = np.arange(npts/2+1)/(float(npts)/fs)

    # set up calibration parameters to test
    calibration_methods = []
    # generate unsmoothed calibration attenuation vector
    noise_curve_db = attenuation_curve(wn_signal, mean_control_noise, fs, calf, SMOOTHING)

    info = {'signal':'noise'}
    if MULT_CAL:
        info['method'] =  'multiply'
        info['truncation'] = None
        info['len'] = len(noise_curve_db)
        info['calibration'] = noise_curve_db
        calibration_methods.append(info.copy())


    if CONV_CAL:
        info['method'] =  'convolve'
        for trunc in TRUNCATIONS:
            info['truncation'] = trunc
            ir = impulse_response(fs, noise_curve_db, freqs, frange, trunc)
            info['len'] = len(ir)
            info['calibration'] = ir
            calibration_methods.append(info.copy())

    chirp = FMSweep()
    chirp.setDuration(dur)
    chirp.setIntensity(80)
    chirp_signal = chirp.signal(fs, 0, refdb, refv)

    vocal_fs = 375000
    tempfile = os.path.join(os.path.expanduser('~'), 'EjM_Vox_plus.json')
    with open(tempfile, 'r') as fh:
        savedstim = json.load(fh)
    stim = StimulusModel.loadFromTemplate(savedstim)
    stim.setReferenceVoltage(110, 1.0)
    vocal_signal = stim.signal()[0]

    for cal_params in calibration_methods:
        start = time.time()
        for i in range(nsignals):
            wn_signal_calibrated = apply_calibration(chirp_signal, fs, frange, 
                                                     freqs, cal_params['calibration'],
                                                     cal_params['method'])
        tdif = time.time() - start
        cal_params['chirp_time'] = tdif

    for cal_params in calibration_methods:
        start = time.time()
        for i in range(nsignals):
            chirp_signal_calibrated = apply_calibration(vocal_signal, vocal_fs, frange, 
                                                 freqs, cal_params['calibration'],
                                                 cal_params['method'])
        tdif = time.time() - start
        cal_params['vocal_time'] = tdif

#####################################
# Report results
#####################################
    app = QtGui.QApplication(sys.argv)

    
# Table of results error =======================

    column_headers = ['method', 'signal', 'truncation', 'len', 'vocal_time', 'chirp_time']
    table = QtGui.QTableWidget(len(calibration_methods), len(column_headers))
    table.setHorizontalHeaderLabels(column_headers)

    print 'number of cal_params', len(calibration_methods)
    irow = 0
    for cal_params in calibration_methods:
        for icol, col in enumerate(column_headers):
            item = MyTableWidgetItem(str(cal_params[col]))
            table.setItem(irow, icol, item)
        irow +=1

    table.setSortingEnabled(True)
    table.show()
    sys.exit(app.exec_())