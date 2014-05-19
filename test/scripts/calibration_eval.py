import sys, time
import numpy as np

from spikeylab.io.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import WhiteNoise, PureTone, FMSweep
from spikeylab.plotting.pyqtgraph_widgets import StackedPlot
from spikeylab.tools.audiotools import tukey, calc_impulse_response, \
                convolve_filter, smooth, calc_attenuation_curve, multiply_frequencies, \
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

MULT_CAL = False
CONV_CAL = True
NOISE_CAL = False
CHIRP_CAL = True

# SMOOTHINGS = [0, 11, 55, 99, 155, 199]
SMOOTHINGS = [99]
TRUNCATIONS = [4]
# TRUNCATIONS = [1, 4, 16, 32, 64, 100]

TONE_CURVE = True
PLOT_RESULTS = True

# method 1 Tone Curve
refv = 0.1 # Volts
refdb = 90 # dB SPL
calf = 15000
dur = 0.1 #seconds (window and stim)
fs = 5e5

if __name__ == "__main__":
    tone_frequencies = range(5000, 100000, 2000)
    # tone_frequencies = [5000, calf, 50000, 100000]
    tone_intensities = [50, 60, 70, 80, 90, 100]
    frange = [2000, 105000] # range to apply calibration to
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

    chirp = FMSweep()
    chirp.setDuration(dur)
    chirp.setIntensity(refdb)
    chirp.setStopFrequency(102000)
    chirp_signal = chirp.signal(fs, 0, refdb, refv)

    # control stim, witout calibration
    print 'control chirp...'

    mean_control_chirp = record(player, chirp_signal, fs)

    freqs = np.arange(npts/2+1)/(float(npts)/fs)

    # set up calibration parameters to test
    calibration_methods = []
    if NOISE_CAL:
        # generate unsmoothed calibration attenuation vector
        noise_curve_db = calc_attenuation_curve(wn_signal, mean_control_noise, fs, calf, smooth_pts=0)

        info = {'signal':'noise'}
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
                    impulse_response = calc_impulse_response(fs, smoothed_attenuations, freqs, frange, trunc)
                    info['len'] = len(impulse_response)
                    info['calibration'] = impulse_response
                    calibration_methods.append(info.copy())


    if CHIRP_CAL:
            
        chirp_curve_db = calc_attenuation_curve(chirp_signal, mean_control_chirp, fs, calf, smooth_pts=0)
        chirp_curve_db -= chirp_curve_db[freqs == calf]
        info = {'signal':'chirp'}
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
                    impulse_response = calc_impulse_response(fs, smoothed_attenuations, freqs, frange, trunc)
                    info['len'] = len(impulse_response)
                    info['calibration'] = impulse_response
                    calibration_methods.append(info.copy())

    print 'number of cals to perform', len(calibration_methods)
    if TONE_CURVE:

        tone = PureTone()
        tone.setDuration(dur)
        tone.setRisefall(0.003)
        vfunc = np.vectorize(calc_db)

        print 'testing calibration curve noise...'
        counter = 0
        for cal_params in calibration_methods:
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
    wn_signal = wn.signal(fs, 0, refdb, refv)
    chirp.setIntensity(60)
    chirp.setStopFrequency(100000)
    chirp_signal = chirp.signal(fs, 0, refdb, refv)

    for cal_params in calibration_methods:
        start = time.time()
        wn_signal_calibrated = apply_calibration(wn_signal, fs, frange, 
                                                 freqs, cal_params['calibration'],
                                                 cal_params['method'])
        tdif = time.time() - start
        mean_response = record(player, wn_signal_calibrated, fs)
        cal_params['noise_response'] = mean_response
        cal_params['time'] = tdif

    for cal_params in calibration_methods:
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
    app = QtGui.QApplication(sys.argv)

    if PLOT_RESULTS:
        if TONE_CURVE:
            fig0 = StackedPlot()
            for cal_params in calibration_methods:
                fig0.add_plot(tone_frequencies, cal_params['tone_curve'], 
                             title='Tones {}, {}, sm:{}, trunc:{}'.format(cal_params['method'],
                             cal_params['signal'], cal_params['smoothing'], 
                              cal_params['truncation']))
            fig0.setWindowTitle('Tone curve')
            fig0.show()

        fig1 = StackedPlot()
        spectrum = abs(np.fft.rfft(wn_signal)/npts)
        spectrum = refdb + 20 * np.log10(spectrum/ refv)
        fig1.add_plot(freqs, spectrum, title='desired')
        for cal_params in calibration_methods:
            spectrum = abs(np.fft.rfft(cal_params['noise_response'])/npts)
            spectrum = 94 + (20.*np.log10((spectrum/np.sqrt(2))/0.004))
            rms = np.sqrt(np.mean(pow(cal_params['chirp_response'],2))) / np.sqrt(2)
            masterdb = 94 + (20.*np.log10(rms/(0.004)))
            print 'noise received overall db', masterdb
            # spectrum[0] = 0
            fig1.add_plot(freqs, spectrum, title='{}, {}, sm:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['truncation']))
        fig1.setWindowTitle('Noise stim')
        fig1.show()

        fig2 = StackedPlot()
        spectrum = abs(np.fft.rfft(chirp_signal)/npts)
        spectrum = refdb + 20 * np.log10(spectrum/ refv)
        # fig2.add_plot(freqs, spectrum, title='desired')
        fig2.add_spectrogram(chirp_signal, fs, title='desired')
        for cal_params in calibration_methods:
            ttl = '{}, {}, sm:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['truncation'])
            fig2.add_spectrogram(cal_params['chirp_response'], fs, title=ttl)
            # spectrum = abs(np.fft.rfft(cal_params['chirp_response'])/npts)
            # spectrum = 94 + (20.*np.log10((spectrum/np.sqrt(2))/0.004))
            # rms = np.sqrt(np.mean(pow(cal_params['chirp_response'],2))) / np.sqrt(2)
            # masterdb = 94 + (20.*np.log10(rms/(0.004)))
            # spectrum[0] = 0
            # fig2.add_plot(freqs, spectrum, title=ttl)
            print 'chirp received overall db', masterdb
        fig2.setWindowTitle('Chirp stim')
        fig2.show()

# Table of results error =======================

    column_headers = ['method', 'signal', 'smoothing', 'truncation', 'len', 'MAE', 'NMSE', 'RMSE', 'time', 'test signal']
    table = QtGui.QTableWidget(len(calibration_methods)*2, len(column_headers))
    table.setHorizontalHeaderLabels(column_headers)

    print 'number of cal_params', len(calibration_methods)
    irow = 0
    for cal_params in calibration_methods:
        if 'noise_response' in cal_params:
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