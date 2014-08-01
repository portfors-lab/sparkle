import sys, time
import numpy as np

from spikeylab.acq.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import WhiteNoise, PureTone, FMSweep
from spikeylab.gui.plotting.pyqtgraph_widgets import StackedPlot
from spikeylab.tools.audiotools import tukey, impulse_response, \
                convolve_filter, smooth, attenuation_curve, multiply_frequencies, \
                calc_db

from test.scripts.util import calc_error, record, MyTableWidgetItem

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
NOISE_CAL = False
CHIRP_CAL = True

# SMOOTHINGS = [99]
# SMOOTHINGS = [0, 11, 55, 99, 155, 199]
SMOOTHINGS = [0, 99, 199, 999]
# TRUNCATIONS = [64]
# TRUNCATIONS = [1, 4, 16, 32, 64, 100]
TRUNCATIONS = [1, 4, 32, 100, 500]
DURATIONS = [0.2]
# DURATIONS = [0.1, 0.2, 0.5, 1.0]
SAMPLERATES = [5e5]
# SAMPLERATES = [2e5, 3e5, 4e5, 5e5]

TONE_CURVE = False
PLOT_RESULTS = True

# method 1 Tone Curve
refv = 2.0 # Volts
refdb = 91 # dB SPL
calf = 15000

if __name__ == "__main__":
    tone_frequencies = range(5000, 100000, 2000)
    # tone_frequencies = [5000, calf, 50000, 100000]
    tone_intensities = [50, 60, 70, 80, 90, 100]
    frange = [2000, 105000] # range to apply calibration to

    player = FinitePlayer()
    player.set_aochan(u"PCI-6259/ao0")
    player.set_aichan(u"PCI-6259/ai0")

    if not CONV_CAL and not MULT_CAL:
        print 'Must choose at lease one calibration type'
        sys.exit()

    wn = WhiteNoise()
    chirp = FMSweep()
    # set up calibration parameters to test
    noise_signals = {}
    chirp_signals = {}
    freqq = {}
    for dur in DURATIONS:
        for fs in SAMPLERATES:
            npts = dur*fs
            player.set_aidur(dur)
            player.set_aisr(fs)

            ##################################
            # white noise test
            wn.setDuration(dur)
            wn.setIntensity(refdb)
            wn_signal = wn.signal(fs, 0, refdb, refv)

            # control stim, witout calibration
            print 'control noise...'

            mean_control_noise = record(player, wn_signal, fs)
            noise_signals[(dur, fs)] = (wn_signal, mean_control_noise)

            chirp.setDuration(dur)
            chirp.setIntensity(refdb)
            chirp.setStopFrequency(102000)
            chirp_signal = chirp.signal(fs, 0, refdb, refv)

            # control stim, witout calibration
            print 'control chirp...'

            mean_control_chirp = record(player, chirp_signal, fs)
            chirp_signals[(dur, fs)] = (chirp_signal, mean_control_chirp)

            freqs = np.arange(npts/2+1)/(float(npts)/fs)
            freqq[(dur, fs)] = freqs

    calibration_methods = [] 
    if NOISE_CAL:
        for durfs, signals in noise_signals.items():
            # generate unsmoothed calibration attenuation vector
            noise_curve_db = attenuation_curve(signals[0], signals[1], durfs[1], calf, smooth_pts=0)
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


            if CONV_CAL:
                info['method'] =  'convolve'
                for sm in SMOOTHINGS:
                    smoothed_attenuations = smooth(noise_curve_db, sm)
                    info['smoothing'] = sm
                    for trunc in TRUNCATIONS:
                        info['truncation'] = trunc
                        ir = impulse_response(fs, smoothed_attenuations, freqs, frange, trunc)
                        info['len'] = len(ir)
                        info['calibration'] = ir
                        calibration_methods.append(info.copy())


    if CHIRP_CAL:
        for durfs, signals in chirp_signals.items():
            
            chirp_curve_db = attenuation_curve(signals[0], signals[1], durfs[1], calf, smooth_pts=0)
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
                    for trunc in TRUNCATIONS:
                        info['truncation'] = trunc
                        ir = impulse_response(fs, smoothed_attenuations, freqs, frange, trunc)
                        info['len'] = len(ir)
                        info['calibration'] = ir
                        calibration_methods.append(info.copy())

    print 'number of cals to perform', len(calibration_methods)
    if TONE_CURVE:

        tone = PureTone()
        tone.setRisefall(0.003)
        vfunc = np.vectorize(calc_db)

        print 'testing calibration curve noise...'
        counter = 0
        for cal_params in calibration_methods:
            dur = cal_params['durfs'][0]
            fs = cal_params['durfs'][1]
            freqs = freqq[cal_params['durfs']]
            npts = dur*fs
            player.set_aidur(dur)
            player.set_aisr(fs)
            tone.setDuration(dur)

            testpeaks = np.zeros((len(tone_intensities), len(tone_frequencies)))
            print 'running tone curve {}/{}'.format(counter, len(cal_params)),
            counter +=1

            tone.setIntensity(refdb)
            tone.setFrequency(calf)
            tone_signal = tone.signal(fs, 0, refdb, refv)
            mean_response = record(player, tone_signal, fs)
            spectrum = np.fft.rfft(mean_response)/npts
            ftp = spectrum[freqs == calf][0]
            test_peak= abs(ftp)
            
            for db_idx, ti in enumerate(tone_intensities):
                tone.setIntensity(ti)
                for freq_idx, tf in enumerate(tone_frequencies):
                    sys.stdout.write('.') # print without spaces
                    reps = []
                    tone.setFrequency(tf)
                    calibrated_tone = apply_calibration(tone.signal(fs, 0, refdb, refv), 
                                            fs, frange, freqs, cal_params['calibration'],
                                            cal_params['method'])
                    mean_response = record(player, calibrated_tone, fs)
                    spectrum = np.fft.rfft(mean_response)/npts
                    ftp = spectrum[freqs == tf][0]
                    mag = abs(ftp)
                    testpeaks[db_idx, freq_idx] = mag

            testcurve_db = vfunc(testpeaks, test_peak) + refdb
            cal_params['tone_curve'] = testcurve_db
            print

        print '\ntest curves finished'

    print 'calibrating vf noise...'

    wn.setIntensity(60)
    chirp.setIntensity(60)
    chirp.setStopFrequency(100000)

    # for cal_params in calibration_methods:
    #     dur = cal_params['durfs'][0]
    #     fs = cal_params['durfs'][1]
    #     freqs = freqq[cal_params['durfs']]
    #     wn.setDuration(dur)
    #     wn_signal = wn.signal(fs, 0, refdb, refv)
    #     player.set_aidur(dur)
    #     player.set_aisr(fs)

    #     start = time.time()
    #     wn_signal_calibrated = apply_calibration(wn_signal, fs, frange, 
    #                                              freqs, cal_params['calibration'],
    #                                              cal_params['method'])
    #     tdif = time.time() - start
    #     mean_response = record(player, wn_signal_calibrated, fs)
    #     cal_params['noise_response'] = mean_response
    #     cal_params['time'] = tdif

    for cal_params in calibration_methods:
        dur = cal_params['durfs'][0]
        fs = cal_params['durfs'][1]
        freqs = freqq[cal_params['durfs']]
        chirp.setDuration(dur)
        chirp_signal = chirp.signal(fs, 0, refdb, refv)
        player.set_aidur(dur)
        player.set_aisr(fs)

        start = time.time()
        chirp_signal_calibrated = apply_calibration(chirp_signal, fs, frange, 
                                                 freqs, cal_params['calibration'],
                                                 cal_params['method'])
        tdif = time.time() - start
        mean_response = record(player, chirp_signal_calibrated, fs)
        cal_params['chirp_response'] = mean_response
        cal_params['time'] = tdif

#####################################
# Report results
#####################################

    # add uncalibrated to table
    for durfs, signals in chirp_signals.items():
        info = {'signal':'chrip', 'durfs': durfs, 'method': None, 
                'truncation':None, 'len':0, 'smoothing':None,
                'time':0}
        info['chirp_response'] = signals[1]
        info['noise_response'] = mean_control_noise
        calibration_methods.append(info)


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

        # fig1 = StackedPlot()
        # spectrum = abs(np.fft.rfft(wn_signal)/npts)
        # spectrum = refdb + 20 * np.log10(spectrum/ refv)
        # fig1.addPlot(freqs, spectrum, title='desired')
        # for cal_params in calibration_methods:
        #     dur = cal_params['durfs'][0]
        #     fs = cal_params['durfs'][1]
        #     npts = dur*fs
        #     spectrum = abs(np.fft.rfft(cal_params['noise_response'])/npts)
        #     spectrum = 94 + (20.*np.log10((spectrum/np.sqrt(2))/0.004))
        #     rms = np.sqrt(np.mean(pow(cal_params['noise_response'],2))) / np.sqrt(2)
        #     masterdb = 94 + (20.*np.log10(rms/(0.004)))
        #     print 'noise received overall db', masterdb
        #     # spectrum[0] = 0
        #     freqs = freqq[cal_params['durfs']]
        #     fig1.addPlot(freqs, spectrum, title='{}, {}, sm:{}, trunc:{}'.format(cal_params['method'], 
        #               cal_params['signal'], cal_params['smoothing'], 
        #               cal_params['truncation']))
        # fig1.setWindowTitle('Noise stim')
        # fig1.show()

        fig2 = StackedPlot()
        spectrum = abs(np.fft.rfft(chirp_signal)/npts)
        spectrum = refdb + 20 * np.log10(spectrum/ refv)
        fig2.addPlot(freqs, spectrum, title='desired')
        # fig2.addSpectrogram(chirp_signal, fs, title='desired')
        for cal_params in calibration_methods:
            freqs = freqq[cal_params['durfs']]
            fs = cal_params['durfs'][1]
            ttl = '{}, {}, sm:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['truncation'])
            # fig2.addSpectrogram(cal_params['chirp_response'], fs, title=ttl)
            spectrum = abs(np.fft.rfft(cal_params['chirp_response'])/npts)
            spectrum = 94 + (20.*np.log10((spectrum/np.sqrt(2))/0.004))
            rms = np.sqrt(np.mean(pow(cal_params['chirp_response'],2))) / np.sqrt(2)
            masterdb = 94 + (20.*np.log10(rms/(0.004)))
            spectrum[0] = 0
            fig2.addPlot(freqs, spectrum, title=ttl)
            print 'chirp received overall db', masterdb
        fig2.setWindowTitle('Chirp stim')
        fig2.show()

# Table of results error =======================

    column_headers = ['method', 'signal', 'durfs', 'smoothing', 'truncation', 'len', 'MAE', 'NMSE', 'RMSE', 'time', 'test signal']
    table = QtGui.QTableWidget(len(calibration_methods)*2, len(column_headers))
    table.setHorizontalHeaderLabels(column_headers)

    print 'number of cal_params', len(calibration_methods)
    irow = 0
    for cal_params in calibration_methods:
        dur = cal_params['durfs'][0]
        fs = cal_params['durfs'][1]
        freqs = freqq[cal_params['durfs']]
        if 'noise_response' in cal_params:
            wn_signal = noise_signals[(dur, fs)][0]
            ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(wn_signal, cal_params['noise_response'], fs, frange, refdb, refv)
            cal_params['MAE'] = ctrl_mae
            cal_params['NMSE'] = ctrl_err
            cal_params['RMSE'] = ctrl_err_sr
            for icol, col in enumerate(column_headers[:-1]):
                item = MyTableWidgetItem(str(cal_params[col]))
                table.setItem(irow, icol, item)
            item = QtGui.QTableWidgetItem('noise')
            table.setItem(irow, icol+1, item)
            irow +=1

        if 'chirp_response' in cal_params:
            chirp_signal = chirp_signals[(dur, fs)][0]

            ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(chirp_signal, cal_params['chirp_response'], fs, frange, refdb, refv)
            cal_params['MAE'] = ctrl_mae
            cal_params['NMSE'] = ctrl_err
            cal_params['RMSE'] = ctrl_err_sr
            for icol, col in enumerate(column_headers[:-1]):
                item = MyTableWidgetItem(str(cal_params[col]))
                table.setItem(irow, icol, item)
            item = QtGui.QTableWidgetItem('chirp')
            table.setItem(irow, icol+1, item)
            irow +=1

    table.setSortingEnabled(True)
    table.show()
    sys.exit(app.exec_())