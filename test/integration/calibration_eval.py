from spikeylab.io.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import WhiteNoise, PureTone, FMSweep
from spikeylab.plotting.pyqtgraph_widgets import StackedPlot
from spikeylab.tools.audiotools import tukey, calc_impulse_response, \
                convolve_filter, smooth, calc_attenuation_curve, multiply_frequencies

import sys, time
import numpy as np

from PyQt4 import QtGui, QtCore

class MyTableWidgetItem(QtGui.QTableWidgetItem):
    def __lt__(self, other):
        try:
            return float(self.text()) < float(other.text())
        except:
            return super(MyTableWidgetItem, self).__lt__(other)

def calc_db(peak, calpeak):
    pbdb = 94 + (20.*np.log10((peak/np.sqrt(2))/0.00407))
    # pbdB = 20 * np.log10(peak/calpeak)
    return pbdb

def calc_error(predicted, recorded, frange, title=None):
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
    predicted_db = refdb + 20 * np.log10(predicted_roi/ refv)
    # recorded_db = calc_db(recorded_roi,0)
    recorded_db = 94 + (20.*np.log10((recorded_roi/np.sqrt(2))/0.004))

    mse = (np.sum((recorded_db - predicted_db)**2))/npts
    mae = abs(np.mean(recorded_db - predicted_db))
    mse2 = np.sqrt(mse)

    # plt.figure()
    # plt.suptitle('{} {:.4f}'.format(title, mse2))
    # plt.subplot(211)
    # plt.plot(f[f0:f1], predicted_db)
    # plt.title("predicted")
    # plt.subplot(212)
    # plt.title("recorded")
    # plt.plot(f[f0:f1], recorded_db)
    # plt.show()

    return mse, mse2, mae

def apply_calibration(sig, fs, frange, calfqs, calvals, method):
    if method == 'multiply':
        return multiply_frequencies(sig, fs, frange, calfqs, calvals)
    elif method == 'convolve':
        return convolve_filter(sig, calvals)
    else:
        raise Exception("Unknown calibration method: {}".format(method))


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


MULT_CAL = True
CONV_CAL = True
NOISE_CAL = True
CHIRP_CAL = False

# SMOOTHINGS = [0, 11, 55, 99, 155, 199]
SMOOTHINGS = [99]
# TRUNCATIONS = [4]
# TRUNCATIONS = [1, 2, 4, 8]
TRUNCATIONS = [1, 4, 16, 32, 64, 100]

TONE_CURVE = False
PLOT_RESULTS = True

# method 1 Tone Curve
nreps = 3
refv = 1.2 # Volts
refdb = 115 # dB SPL
calf = 15000
dur = 0.2 #seconds (window and stim)
fs = 5e5

if __name__ == "__main__":
    # tone_frequencies = range(5000, 110000, 2000)
    tone_frequencies = [5000, calf, 50000, 100000]
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

    mean_control_noise = record(wn_signal)

    chirp = FMSweep()
    chirp.setDuration(dur)
    chirp.setIntensity(refdb)
    chirp_signal = chirp.signal(fs, 0, refdb, refv)

    # control stim, witout calibration
    print 'control chirp...'

    mean_control_chirp = record(chirp_signal)

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
                    impulse_response = calc_impulse_response(smoothed_attenuations, freqs, frange, trunc)
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
                    impulse_response = calc_impulse_response(smoothed_attenuations, freqs, frange, trunc)
                    info['len'] = len(impulse_response)
                    info['calibration'] = impulse_response
                    calibration_methods.append(info.copy())

    print 'number of cals to perform', len(calibration_methods)
    if TONE_CURVE:

        tone = PureTone()
        tone.setDuration(dur)
        tone.setRisefall(0.003)
        tone.setIntensity(80)
        # tone.setIntensity(refdb)
        vfunc = np.vectorize(calc_db)

        print 'testing calibration curve noise...'
        counter = 0
        for cal_params in calibration_methods:
            testpeaks = []
            print 'running tone curve {}/{}'.format(counter, len(cal_params)),
            counter +=1
            for tf in tone_frequencies:
                sys.stdout.write('.') # print without spaces
                reps = []
                tone.setFrequency(tf)
                calibrated_tone = apply_calibration(tone.signal(fs, 0, refdb, refv), 
                                        fs, frange, freqs, cal_params['calibration'],
                                        cal_params['method'])
                mean_response = record(calibrated_tone)
                spectrum = np.fft.rfft(mean_response)/npts
                ftp = spectrum[freqs == tf][0]
                mag = abs(ftp)
                testpeaks.append(mag)

            test_peak = testpeaks[tone_frequencies.index(calf)]
            testcurve_db = vfunc(testpeaks, test_peak)
            cal_params['tone_curve'] = testcurve_db
            print

        print '\ntest curves finished'

    print 'calibrating vf noise...'

    wn.setIntensity(80)
    wn_signal = wn.signal(fs, 0, refdb, refv)
    chirp.setIntensity(80)
    chirp_signal = chirp.signal(fs, 0, refdb, refv)

    for cal_params in calibration_methods:
        start = time.time()
        wn_signal_calibrated = apply_calibration(wn_signal, fs, frange, 
                                                 freqs, cal_params['calibration'],
                                                 cal_params['method'])
        tdif = time.time() - start
        mean_response = record(wn_signal_calibrated)
        cal_params['noise_response'] = mean_response
        cal_params['time'] = tdif

    for cal_params in calibration_methods:
        start = time.time()
        chirp_signal_calibrated = apply_calibration(chirp_signal, fs, frange, 
                                                 freqs, cal_params['calibration'],
                                                 cal_params['method'])
        tdif = time.time() - start
        mean_response = record(chirp_signal_calibrated)
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
            # spectrum[0] = 0
            fig1.add_plot(freqs, spectrum, title='{}, {}, sm:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['truncation']))
        fig1.setWindowTitle('Noise stim')
        fig1.show()

        fig2 = StackedPlot()
        spectrum = abs(np.fft.rfft(chirp_signal)/npts)
        spectrum = refdb + 20 * np.log10(spectrum/ refv)
        fig2.add_plot(freqs, spectrum, title='desired')
        # fig2.add_spectrogram(chirp_signal, fs, title='desired')
        for cal_params in calibration_methods:
            ttl = '{}, {}, sm:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['truncation'])
            # fig2.add_spectrogram(cal_params['chirp_response'], fs, title=ttl)
            spectrum = abs(np.fft.rfft(cal_params['chirp_response'])/npts)
            spectrum = 94 + (20.*np.log10((spectrum/np.sqrt(2))/0.004))
            rms = np.sqrt(np.mean(pow(cal_params['chirp_response'],2))) / np.sqrt(2)
            masterdb = 94 + (20.*np.log10(rms/(0.004)))
            print 'received overall db', masterdb
            # spectrum[0] = 0
            fig2.add_plot(freqs, spectrum, title=ttl)
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
            ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(wn_signal, cal_params['noise_response'], frange)
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
            ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(chirp_signal, cal_params['chirp_response'], frange)
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