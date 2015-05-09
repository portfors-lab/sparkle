"""Evalues the calibration procedure for efficacy, allowing manipulation
of many different parameter that could affect this. Measures the error
betweent the desired and recorded signals. Produces a table and plots of 
results.
"""

import sys
import time

import numpy as np
import pyqtgraph as pg

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.acq.players import FinitePlayer
from sparkle.gui.plotting.pyqtgraph_widgets import SimplePlotWidget, \
    StackedPlot
from sparkle.stim.types.stimuli_classes import FMSweep, PureTone, WhiteNoise
from sparkle.tools.audiotools import attenuation_curve, calc_db, \
    calc_spectrum, impulse_response, signal_amplitude, smooth, tukey
from test.scripts.util import MyTableWidgetItem, apply_calibration, \
    calc_error, record, run_tone_curve, record_refdb

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
############################################################
# Edit these values as desired

MPHONESENS = 0.109
MPHONECALDB = 94

MULT_CAL = False
CONV_CAL = True
NOISE_CAL = False
CHIRP_CAL = True

# SMOOTHINGS = [11, 99]
SMOOTHINGS = [0, 11, 55, 99, 155, 199]
# SMOOTHINGS = [0, 7, 63, 99]
DURATIONS = [0.05]
# DURATIONS = [0.1, 0.2, 0.5, 1.0]
SAMPLERATES = [5e5]
# FILTER_LEN = [2**10, 2**11, 2**12, 2**14, 2**15, 2**16, 0.2*5e5]
FILTER_LEN = range(50, 8500, 50)
FILTER_LEN = [2**14]
# SAMPLERATES = [2e5, 3e5, 4e5, 5e5]

TONE_CURVE = False
PLOT_RESULTS = True

refv = 0.5 # Volts
refdb = None #TBD
calf = 17000

test_intensity = 60
    
if __name__ == "__main__":

    # for running a manual calibration curve. Gets a measure of how
    # acurate the intensity calculation is (for pure tones at least)
    tone_frequencies = range(5000, 100000, 2000)
    # tone_frequencies = [5000, calf, 50000, 100000]
    # tone_intensities = [50, 60, 70, 80, 90, 100]
    tone_intensities = [50, 60]
    frange = [3750, 101250] # range to apply calibration to

    player = FinitePlayer()
    player.set_aochan(u"PCI-6259/ao0")
    player.set_aichan(u"PCI-6259/ai0")

    if not CONV_CAL and not MULT_CAL:
        print 'Must choose at least one calibration type'
        sys.exit()

    wn = WhiteNoise()
    chirp = FMSweep()

    # get the reference db for given voltage
    refdb = record_refdb(player, calf, refv, 5e5)
    # check it back!
    # dur = 0.2
    # reftone = PureTone()
    # reftone.setRisefall(0.003)
    # reftone.setDuration(dur)
    # reftone.setIntensity(60)
    # reftone.setFrequency(calf)
    # tempfs = 5e5
    # ref_db_signal = reftone.signal(tempfs, 0, refdb, refv)
    # player.set_aidur(dur)
    # player.set_aifs(tempfs)
    # ref_db_response = record(player, ref_db_signal, tempfs)
    # checkdb = calc_db(signal_amplitude(ref_db_response, tempfs), MPHONESENS, MPHONECALDB)
    # print "CHECK DB 60: ", checkdb

    # record the intital sound to determine the frequency 
    # response from. Use both noise and chirp, and include 
    # all the different combinations of duration and samplerate.
    noise_signals = {}
    chirp_signals = {}
    freqq = {}
    for dur in DURATIONS:
        for fs in SAMPLERATES:
            npts = dur*fs
            player.set_aidur(dur)
            player.set_aifs(fs)

            # White Noise
            wn.setDuration(dur)
            wn.setIntensity(test_intensity)
            wn_signal = wn.signal(fs, 0, refdb, refv)

            # control stim, witout calibration
            print 'control noise...'

            mean_control_noise = record(player, wn_signal, fs)
            # store this is in a dict for later
            noise_signals[(dur, fs)] = (wn_signal, mean_control_noise)

            # Frequency Modulated Sweep
            chirp.setDuration(dur)
            chirp.setIntensity(test_intensity)
            chirp.setStartFrequency(4000)
            chirp.setStopFrequency(101000)
            chirp_signal = chirp.signal(fs, 0, refdb, refv)

            # control stim, witout calibration
            print 'control chirp...'

            mean_control_chirp = record(player, chirp_signal, fs)
            # store this is in a dict for later
            chirp_signals[(dur, fs)] = (chirp_signal, mean_control_chirp)

            # also store the matching frequencies for when the frequency
            # response is calculated with this particular duration and
            # samplerate combo
            freqs = np.arange(npts/2+1)/(float(npts)/fs)
            freqq[(dur, fs)] = freqs

    # create dicts that collect all the test run parameters that we can then
    # just loop through and time the execution for calibrations with the 
    # contained parameters makes for simpler reporting later
    calibration_methods = []
    # using noise to determine the frequency response 
    if NOISE_CAL:
        for durfs, signals in noise_signals.items():
            # generate unsmoothed calibration attenuation vector
            noise_curve_db = attenuation_curve(signals[0], signals[1], 
                                        durfs[1], calf, smooth_pts=0)
            freqs = freqq[durfs]
            noise_curve_db -= noise_curve_db[freqs == calf]
            info = {'signal':'noise', 'durfs': durfs}

            if MULT_CAL:
                info['method'] =  'multiply'
                info['truncation'] = None
                info['len'] = len(noise_curve_db)
                for sm in SMOOTHINGS:
                    smoothed_attenuations = smooth(noise_curve_db, sm)
                    info['smoothing'] = sm
                    info['calibration'] = smoothed_attenuations
                    calibration_methods.append(info.copy())

            # because the impulse response is calculated once in advance, 
            # do that now for each filter length, and save for timed test
            if CONV_CAL:
                info['method'] =  'convolve'
                for sm in SMOOTHINGS:
                    smoothed_attenuations = smooth(noise_curve_db, sm)
                    info['smoothing'] = sm
                    for trunc in FILTER_LEN:
                        info['truncation'] = trunc
                        ir = impulse_response(fs, smoothed_attenuations, freqs, frange, trunc)
                        info['len'] = len(ir)
                        info['calibration'] = ir
                        calibration_methods.append(info.copy())

            # control : no calibration
            info['method'] = None
            info['truncation'] = None
            info['len'] = 0
            info['smoothing'] = None
            info['time'] = 0
            info['calibration'] = None
            calibration_methods.append(info.copy())

    # do the same thing using the chirp signal to determine the frequency response
    if CHIRP_CAL:
        for durfs, signals in chirp_signals.items():
            chirp_curve_db = attenuation_curve(signals[0], signals[1], 
                                        durfs[1], calf, smooth_pts=0)
            freqs = freqq[durfs]    
            chirp_curve_db -= chirp_curve_db[freqs == calf]
            info = {'signal':'chirp', 'durfs': durfs}
            if MULT_CAL:
                info['method'] =  'multiply'
                info['truncation'] = None
                info['len'] = len(chirp_curve_db)
                for sm in SMOOTHINGS:
                    smoothed_attenuations = smooth(chirp_curve_db, sm)
                    info['smoothing'] = sm
                    info['calibration'] = smoothed_attenuations
                    calibration_methods.append(info.copy())


            if CONV_CAL:
                info['method'] =  'convolve'
                for sm in SMOOTHINGS:
                    smoothed_attenuations = smooth(chirp_curve_db, sm)
                    info['smoothing'] = sm
                    for trunc in FILTER_LEN:
                        info['truncation'] = trunc
                        ir = impulse_response(fs, smoothed_attenuations, freqs,
                                              frange, trunc)
                        info['len'] = len(ir)
                        info['calibration'] = ir
                        calibration_methods.append(info.copy())

            # control : no calibration
            info['method'] = None
            info['truncation'] = None
            info['len'] = 0
            info['smoothing'] = None
            info['calibration'] = None
            info['time'] = 0
            calibration_methods.append(info.copy())

    print 'number of cals to perform', len(calibration_methods)
    if TONE_CURVE:

        print 'testing calibration curve...'
        counter = 0
        for cal_params in calibration_methods:
            dur = cal_params['durfs'][0]
            fs = cal_params['durfs'][1]
            freqs = freqq[cal_params['durfs']]

            print 'running tone curve {}/{}'.format(counter, len(calibration_methods)-1),
            counter +=1

            if cal_params['method'] == 'multiply':
                cal = (freqs, cal_params['calibration'])
            else: # convolve or none
                cal = cal_params['calibration']
            testcurve_db = run_tone_curve(tone_frequencies, tone_intensities, 
                                          player, fs, dur, refdb, refv, cal,
                                          frange)[0]
            cal_params['tone_curve'] = testcurve_db
            print #newline

        print 'test curves finished\n'

    errs_list = []
    # run each calibration on a chirp signal
    for cal_params in calibration_methods:
        dur = cal_params['durfs'][0]
        fs = cal_params['durfs'][1]
        freqs = freqq[cal_params['durfs']]
        chirp.setDuration(dur)
        chirp_signal = chirp.signal(fs, 0, refdb, refv)
        player.set_aidur(dur)
        player.set_aifs(fs)

        if cal_params['method'] == 'multiply':
            cal = (freqs, cal_params['calibration'])
        else: # convolve or none
            cal = cal_params['calibration']

        start = time.time()
        chirp_signal_calibrated = apply_calibration(chirp_signal, fs, frange, cal)
        tdif = time.time() - start
        # print 'signal maxes', np.max(abs(chirp_signal)), np.amax(abs(chirp_signal_calibrated))
        mean_response = record(player, chirp_signal_calibrated, fs)
        cal_params['chirp_response'] = mean_response
        cal_params['time'] = tdif
        ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(chirp_signal, 
                                            cal_params['chirp_response'], 
                                            fs, frange, refdb, refv)
        cal_params['MAE'] = ctrl_mae
        cal_params['MSE'] = ctrl_err
        cal_params['RMSE'] = ctrl_err_sr
        errs_list.append(ctrl_err)


    #####################################
    # Report results
    #####################################

    app = QtGui.QApplication(sys.argv)

    if PLOT_RESULTS:
        if TONE_CURVE:
            fig0 = StackedPlot()
            for cal_params in calibration_methods:
                fig0.addPlot(tone_frequencies, cal_params['tone_curve'], 
                             title='Tones {}, {}, sm:{}, trunc:{}'.format(cal_params['method'],
                             cal_params['signal'], cal_params['smoothing'], 
                              cal_params['truncation']))
            fig0.setWindowTitle('Tone curve')
            fig0.show()

        # show all of the chirp results in either signal or spectrogram representation
        fig2 = StackedPlot()
        # just show one desired control signal... whatever the last one was
        freqs, spectrum = calc_spectrum(chirp_signal, fs)
        spectrum = calc_db(spectrum, MPHONESENS, MPHONECALDB)
        fig2.addPlot(freqs, spectrum, title='desired')
        # fig2.addSpectrogram(chirp_signal, fs, title='desired')

        for cal_params in calibration_methods:
            # add a plot for each recorded calibrated signal
            fs = cal_params['durfs'][1]
            ttl = '{}, {}, sm:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['truncation'])

            # fig2.addSpectrogram(cal_params['chirp_response'], fs, title=ttl)

            freqs, spectrum = calc_spectrum(cal_params['chirp_response'], fs)
            # convert spectrum into dB
            spectrum = calc_db(spectrum, MPHONESENS, MPHONECALDB)
            mag = signal_amplitude(cal_params['chirp_response'], fs)
            masterdb = calc_db(mag, MPHONESENS, MPHONECALDB)
            spectrum[0] = 0
            fig2.addPlot(freqs, spectrum, title=ttl)
            print 'chirp received overall db', masterdb
        fig2.setWindowTitle('Chirp stim')
        fig2.show()

    # Table of results error =======================

    column_headers = ['method', 'signal', 'durfs', 'smoothing', 'truncation',
                      'len', 'MAE', 'MSE', 'RMSE', 'time', 'test signal']
    table = QtGui.QTableWidget(len(calibration_methods)*2, len(column_headers))
    table.setHorizontalHeaderLabels(column_headers)

    print 'number of cal_params', len(calibration_methods)
    irow = 0
    for cal_params in calibration_methods:
        dur = cal_params['durfs'][0]
        fs = cal_params['durfs'][1]
        freqs = freqq[cal_params['durfs']]

        if 'chirp_response' in cal_params:
            for icol, col in enumerate(column_headers[:-1]):
                item = MyTableWidgetItem(str(cal_params[col]))
                table.setItem(irow, icol, item)
            item = QtGui.QTableWidgetItem('chirp')
            table.setItem(irow, icol+1, item)
            irow +=1

    table.setSortingEnabled(True)
    table.show()

    # trend_plot = SimplePlotWidget(FILTER_LEN, errs_list[1:-1])
    # trend_plot.show()

    # pw = pg.PlotWidget()
    # err_idx = 0
    # if MULT_CAL:
    #     # first error is for multiplication calibration, last is uncalibrated
    #     pw.plot([FILTER_LEN[-1]], [errs_list[err_idx]], symbol='x', symbolPen='b')
    #     err_idx += 1
    # if CONV_CAL:
    #     pw.plot(FILTER_LEN, errs_list[err_idx:-1], pen={'color':'b', 'width':3})
    # style = {'font-size':'16pt'}
    # pw.setLabel('left', 'Distance from Desired Signal (MSE)', **style)
    # pw.setLabel('bottom', 'Filter Length (no. of samples)', **style)
    # pw.setTitle('<span style="font-size:20pt">Filter Length Effect on Calibration Efficacy</span>', **style)
    # font = QtGui.QFont()
    # font.setPointSize(12)
    # pw.getAxis('bottom').setTickFont(font)
    # pw.getAxis('left').setTickFont(font)
    # pw.show()

    sys.exit(app.exec_())
