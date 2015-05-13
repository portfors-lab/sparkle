"""Evaluates the calibration procedure for execution time for different 
algorithms and parameter values
"""

import json
import os
import sys
import time

import numpy as np
import pyqtgraph as pg

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.acq.players import FinitePlayer
from sparkle.stim.stimulus_model import StimulusModel
# from sparkle.gui.plotting.pyqtgraph_widgets import SimplePlotWidget
from sparkle.stim.types.stimuli_classes import FMSweep, WhiteNoise
from sparkle.tools.audiotools import attenuation_curve, impulse_response
from test.scripts.util import MyTableWidgetItem, apply_calibration, \
    calc_error, record, record_refdb

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
############################################################
# Edit these values as desired

MULT_CAL = True # include the multiplication calibration method
CONV_CAL = True # include the convolution calibration method

SMOOTHING = 99 # number of points of a signal to smooth over

nreps = 3 # no. of repetition for each outgoing signal (results will be averaged)
refv = 0.5 # Volts, output amplitdue of the outgoing signal
calf = 15000 # the frequency that was used for refv and refdb
dur = 0.2 # duration of signal and window (seconds)
fs = 5e5 # input and output samplerate
nsignals = 200 # number of signals to run calibration on per sample time

frange = [2000, 105000] # range to apply calibration to

# FILTER_LENS = range(24286, 24292)
FILTER_LENS = [2**6, 2**7, 2**8, 2**9, 2**10, 2**11, 2**12, 2**14, 31072, 31074, 2**15, 2**16, dur*fs]
# FILTER_LENS = range(1000, int(dur*fs), 1000)

if __name__ == "__main__":
    npts = dur*fs

    player = FinitePlayer()
    player.set_aochan(u"PCI-6259/ao0")
    player.set_aichan(u"PCI-6259/ai0")

    # get the reference db for given voltage
    refdb = record_refdb(player, calf, refv, 5e5)

    player.set_aidur(dur)
    player.set_aifs(fs)

    if not CONV_CAL and not MULT_CAL:
        print 'Must choose at lease one calibration type'
        sys.exit()

    # record the intital sound to determine the frequency response from
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
    # generate smoothed calibration attenuation vector
    noise_curve_db = attenuation_curve(wn_signal, mean_control_noise, fs, calf, SMOOTHING)

    # create dicts that collect all the test run parameters that we can then
    # just loop through and time the execution for calibrations with the contained parameters
    # makes for simpler reporting later
    info = {'signal':'noise'}
    if MULT_CAL:
        info['method'] =  'multiply'
        info['truncation'] = None
        info['len'] = len(noise_curve_db)
        info['calibration'] = noise_curve_db
        calibration_methods.append(info.copy())


    # because the impulse response is calculated once in advance, do that now for each
    # filter length, and save for timed test
    if CONV_CAL:
        info['method'] =  'convolve'
        for filter_len in FILTER_LENS:
            info['truncation'] = filter_len
            ir = impulse_response(fs, noise_curve_db, freqs, frange, filter_len)
            info['len'] = len(ir)
            info['calibration'] = ir
            calibration_methods.append(info.copy())

    # get a signal to apply the calibration to
    chirp = FMSweep()
    chirp.setDuration(dur)
    chirp.setIntensity(80)
    chirp_signal = chirp.signal(fs, 0, refdb, refv)

    # use a different sample rate -- one that is present in our
    # vocal recording files
    vocal_fs = 375000
    # pseudo vocal signal
    vocal_signal = chirp.signal(vocal_fs, 0, refdb, refv)

    # Run the timed calibration executions for each test stimulus
    time_list = []
    for cal_params in calibration_methods:
        if cal_params['method'] == 'multiply':
            cal = (freqs, cal_params['calibration'])
        else: # convolve
            cal = cal_params['calibration']
        start = time.time()
        for i in range(nsignals):
            wn_signal_calibrated = apply_calibration(chirp_signal, fs, frange, 
                                                     cal)
        tdif = time.time() - start
        cal_params['chirp_time'] = np.around(tdif,3)
        time_list.append(np.around(tdif,3))

    for cal_params in calibration_methods:
        if cal_params['method'] == 'multiply':
            cal = (freqs, cal_params['calibration'])
        else: # convolve
            cal = cal_params['calibration']
        start = time.time()
        start = time.time()
        for i in range(nsignals):
            chirp_signal_calibrated = apply_calibration(vocal_signal, vocal_fs,
                                                        frange, cal)
        tdif = time.time() - start
        cal_params['vocal_time'] = np.around(tdif,3)

    #####################################
    # Report results
    #####################################
    app = QtGui.QApplication(sys.argv)

    
    # Table of results times =======================

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

    # show a plot for the times results for the calibrated chirp
    # trend_plot = SimplePlotWidget(FILTER_LENS, time_list[1:])
    # trend_plot.show()

    pw = pg.PlotWidget()
    pw.plot(FILTER_LENS, time_list[1:], pen={'color':'b', 'width':3})
    pw.plot([FILTER_LENS[-1]], [time_list[0]], symbol='x', symbolPen='b')
    style = {'font-size':'16pt'}
    pw.setLabel('left', 'Execution time (s)', **style)
    pw.setLabel('bottom', 'Filter Length (no. of samples)', **style)
    pw.setTitle('<span style="font-size:20pt">Filter Length Effect on Calibration Performance</span>', **style)
    font = QtGui.QFont()
    font.setPointSize(12)
    pw.getAxis('bottom').setTickFont(font)
    pw.getAxis('left').setTickFont(font)
    pw.show()

    sys.exit(app.exec_())
