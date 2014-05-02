from spikeylab.io.players import FinitePlayer
from spikeylab.stim.types.stimuli_classes import WhiteNoise, PureTone, FMSweep
from spikeylab.plotting.pyqtgraph_widgets import FFTWidget

import sys, csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import convolve, fftconvolve, hann

from PyQt4 import QtGui

def tukey(winlen, alpha):
    taper = hann(winlen*alpha)
    rect = np.ones(winlen-len(taper) + 1)
    win = fftconvolve(taper, rect)
    win = win / np.amax(win)
    return win

def smooth(x,window_len=99, window='hanning'):

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    elif window == 'kaiser':
        w = np.kaiser(window_len,4)
    else:
        w = eval('np.'+window+'(window_len)')
    y=np.convolve(w/w.sum(),s,mode='valid')
    return y[window_len/2:len(y)-window_len/2]

def calc_db(peak, calpeak):
    pbdb = 94 + (20.*np.log10((peak/np.sqrt(2))/0.00407))
    # pbdB = 20 * np.log10(peak/calpeak)
    return pbdb

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

    # plt.figure()
    # plt.suptitle('{} {:.4f}'.format(title, mse2))
    # plt.subplot(211)
    # plt.plot(f[f0:f1], predicted_roi.real)
    # plt.title("predicted")
    # plt.subplot(212)
    # plt.title("recorded")
    # plt.plot(f[f0:f1], recorded_roi.real)

    return mse, mse2, mae

def apply_calibration(sig, fs, frange, calfqs, calvals, method):
    if method == 'multiply':
        return multiply_frequencies(sig, fs, frange, calfqs, calvals)
    elif method == 'convolve':
        return convolve_impulse(sig, fs, calvals)
    else:
        raise Exception("Unknown calibration method: {}".format(method))

def multiply_frequencies(sig, fs, frange, calfqs, calvals):
    X = np.fft.rfft(sig)

    npts = len(sig)
    f = np.arange(npts/2+1)/(float(npts)/fs)
    f0 = (np.abs(f-frange[0])).argmin()
    f1 = (np.abs(f-frange[1])).argmin()

    # plt.figure()
    # plt.plot(calfqs,calvals)
    # plt.title('cal apply inputs')

    cal_func = interp1d(calfqs, calvals)
    frange = f[f0:f1]
    Hroi = cal_func(frange)
    H = np.zeros((npts/2+1,))
    H[f0:f1] = Hroi
    # plt.figure()
    # plt.plot(f,H)
    # plt.title('H apply cal pre-smoothing')
    H = smooth(H)
    # plt.figure()
    # plt.plot(f,H)
    # plt.title('H apply cal')
    # plt.show()
    # convert to voltage scalars
    H = 10**((H).astype(float)/20)
    # Xadjusted = X.copy()
    # Xadjusted[f0:f1] *= H
    # Xadjusted = smooth(Xadjusted)
    Xadjusted = X*H

    signal_calibrated = np.fft.irfft(Xadjusted)
    return signal_calibrated

def bb_cal_curve(sig, resp, fs, frange):
    """Given original signal and recording, generates a dB attenuation curve"""
    # remove dc offset from recorded response (orignal shouldn't have one)
    dc = np.mean(resp)
    resp = resp - dc

    npts = len(sig)
    f0 = np.ceil(frange[0]/(float(fs)/npts))
    f1 = np.floor(frange[1]/(float(fs)/npts))

    y = resp
    # y = y/np.amax(y) # normalize
    Y = np.fft.rfft(y)

    x = sig
    # x = x/np.amax(x) # normalize
    X = np.fft.rfft(x)
    
    # H = np.where(X.real!=0, Y/X, 1)
    # diffdB = 20 * np.log10(H)

    Ymag = np.sqrt(Y.real**2 + Y.imag**2)
    Xmag = np.sqrt(X.real**2 + X.imag**2)

    YmagdB = 20 * np.log10(Ymag)
    XmagdB = 20 * np.log10(Xmag)

    diffdB = XmagdB - YmagdB


    # fq = np.arange(npts/2+1)/(float(npts)/fs)
    # plt.figure()
    # plt.plot(fq, diffdB)
    # plt.title('diff db in cal funct')
    # plt.show()
    # restrict to desired frequencies and smooth
    # this should probably be done on the other side,
    # before it gets applied.


    # return diffdB[f0:f1], fq[f0:f1]
    return diffdB

def bb_calibration(sig, resp, fs, frange):
    """Given original signal and recording, spits out a calibrated signal"""
    # remove dc offset from recorded response (synthesized orignal shouldn't have one)
    dc = np.mean(resp)
    resp = resp - dc

    npts = len(sig)
    f0 = np.ceil(frange[0]/(float(fs)/npts))
    f1 = np.floor(frange[1]/(float(fs)/npts))

    y = resp
    # y = y/np.amax(y) # normalize
    Y = np.fft.rfft(y)

    x = sig
    # x = x/np.amax(x) # normalize
    X = np.fft.rfft(x)

    # can use magnitude too...
    """
    Ymag = np.sqrt(Y.real**2 + Y.imag**2)
    Xmag = np.sqrt(X.real**2 + X.imag**2)
    # zeros = Xmag == 0
    # Xmag[zeros] = 1
    # Hmag = Ymag/Xmag
    # Xmag[zeros] = 0
    Hmag = np.where(Xmag == 0, 0, Ymag/Xmag)
    Hmag[:f0] = 1
    Hmag[f1:] = 1
    # Hmag = smooth(Hmag)
    """

    H = Y/X

    # still issues warning because all of Y/X is executed to selected answers from
    # H = np.where(X.real!=0, Y/X, 1)
    # H[:f0].real = 1
    # H[f1:].real = 1
    # H = smooth(H)

    A = X / H

    return np.fft.irfft(A)

def calc_ir(db_boost_array, frequencies, frange, decimation=4, truncation=2):
    npoints = len(db_boost_array)
    # fs = (frequencies[1] - frequencies[0]) * (npoints - 1) *2
    # could decimate without interpolating, but leaving in for flexibility
    calc_func = interp1d(frequencies, db_boost_array)
    factor0 = decimation
    # reduce the number of points in the frequency response by factor0 
    decimated_freq = np.arange((npoints)/(factor0))/(float(npoints-1-factor0+(factor0%2))/factor0)*fs/2
    decimated_attenuations = calc_func(decimated_freq)

    f0 = (np.abs(decimated_freq-frange[0])).argmin()
    f1 = (np.abs(decimated_freq-frange[1])).argmin()
    print 'f0, f1', f0, f1

    decimated_attenuations[:f0] = 0
    decimated_attenuations[f1:] = 0
    decimated_attenuations[f0:f1] = decimated_attenuations[f0:f1]*tukey(len(decimated_attenuations[f0:f1]), 0.05)
    freq_response = 10**((decimated_attenuations).astype(float)/20)

    impulse_response = np.fft.irfft(freq_response)
    
    # rotate to create causal filter, and truncate
    impulse_response = np.roll(impulse_response, len(impulse_response)/2)
    factor1 = truncation
    impulse_response = impulse_response[(len(impulse_response)/2)-(len(impulse_response)/factor1/2):(len(impulse_response)/2)+(len(impulse_response)/factor1/2)]
    return impulse_response

def convolve_impulse(signal, fs, impulse_response):
    adjusted_signal = fftconvolve(signal, impulse_response)
    adjusted_signal = adjusted_signal[len(impulse_response)/2:len(adjusted_signal)-len(impulse_response)/2 + 1]
    return adjusted_signal

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
CHIRP_CAL = True

# SMOOTHINGS = [0, 11, 55, 99, 155, 199]
SMOOTHINGS = [99]
# DECIMATIONS = range(1,9)
DECIMATIONS = [4]
TRUNCATIONS = [2]

TONE_CURVE = True
PLOT_RESULTS = True

# method 1 Tone Curve
nreps = 3
refv = 1.2 # Volts
refdb = 115 # dB SPL
calf = 15000
dur = 0.2 #seconds (window and stim)
fs = 5e5

if __name__ == "__main__":
    tone_frequencies = range(5000, 110000, 2000)
    # tone_frequencies = [5000, calf, 50000, 100000]
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
        noise_curve_db = bb_cal_curve(wn_signal, mean_control_noise, fs, frange)
        # shift according to calf
        noise_curve_db -= noise_curve_db[freqs == calf]

        info = {'signal':'noise'}
        if MULT_CAL:
            info['method'] =  'multiply'
            info['decimation'] = None
            info['truncation'] = None
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
                for deci in DECIMATIONS:
                    info['decimation'] = deci
                    for trunc in TRUNCATIONS:
                        info['truncation'] = trunc
                        impulse_response = calc_ir(smoothed_attenuations, freqs, frange, deci, trunc)
                        info['calibration'] = impulse_response
                        calibration_methods.append(info.copy())


    if CHIRP_CAL:
            
        chirp_curve_db = bb_cal_curve(chirp_signal, mean_control_chirp, fs, frange)
        chirp_curve_db -= chirp_curve_db[freqs == calf]
        info = {'signal':'chirp'}
        if MULT_CAL:
            info['method'] =  'multiply'
            info['decimation'] = None
            info['truncation'] = None
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
                for deci in DECIMATIONS:
                    info['decimation'] = deci
                    for trunc in TRUNCATIONS:
                        info['truncation'] = trunc
                        impulse_response = calc_ir(smoothed_attenuations, freqs, frange, deci, trunc)
                        info['calibration'] = impulse_response
                        calibration_methods.append(info.copy())


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

    for cal_params in calibration_methods:

        wn_signal_calibrated = apply_calibration(wn_signal, fs, frange, 
                                                 freqs, cal_params['calibration'],
                                                 cal_params['method'])
        mean_response = record(wn_signal_calibrated)
        cal_params['noise_response'] = mean_response

    for cal_params in calibration_methods:

        chirp_signal_calibrated = apply_calibration(chirp_signal, fs, frange, 
                                                 freqs, cal_params['calibration'],
                                                 cal_params['method'])
        mean_response = record(chirp_signal_calibrated)
        cal_params['chirp_response'] = mean_response

#####################################
# Report results
#####################################
    app = QtGui.QApplication(sys.argv)

    if PLOT_RESULTS:
        nsubplots = len(calibration_methods)
        if TONE_CURVE:
            fig0 = QtGui.QWidget()
            layout = QtGui.QGridLayout()
            pltidx = 0
            for cal_params in calibration_methods:
                subplot = FFTWidget(rotation=0)
                subplot.update_data(tone_frequencies, cal_params['tone_curve'])
                subplot.set_title('Tones {}, {}, sm:{}, deci:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['decimation'], cal_params['truncation']))
                layout.addWidget(subplot, pltidx, 0)
                pltidx +=1
            fig0.setLayout(layout)
            fig0.show()

        fig1 = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        pltidx = 0
        for cal_params in calibration_methods:
            subplot = FFTWidget(rotation=0)
            spectrum = abs(np.fft.rfft(cal_params['noise_response'])/npts)
            spectrum = 94 + (20.*np.log10((spectrum/np.sqrt(2))/0.004))
            spectrum[0] = 0
            subplot.update_data(freqs, spectrum)
            subplot.set_title('{}, {}, sm:{}, deci:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['decimation'], cal_params['truncation']))
            layout.addWidget(subplot, pltidx, 0)
            pltidx +=1
        fig1.setLayout(layout)
        fig1.show()

        fig2 = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        pltidx = 0
        for cal_params in calibration_methods:
            subplot = FFTWidget(rotation=0)
            spectrum = abs(np.fft.rfft(cal_params['chirp_response'])/npts)
            spectrum = 94 + (20.*np.log10((spectrum/np.sqrt(2))/0.004))
            spectrum[0] = 0
            subplot.update_data(freqs, spectrum)
            subplot.set_title('{}, {}, sm:{}, deci:{}, trunc:{}'.format(cal_params['method'], 
                      cal_params['signal'], cal_params['smoothing'], 
                      cal_params['decimation'], cal_params['truncation']))
            layout.addWidget(subplot, pltidx, 0)
            pltidx +=1
        fig2.setLayout(layout)
        fig2.show()

    # Table of results error  

    column_headers = ['method', 'signal', 'smoothing', 'decimation', 'truncation', 'MAE', 'NMSE', 'RMSE', 'test signal']
    table = QtGui.QTableWidget(len(cal_params), len(column_headers))
    table.setHorizontalHeaderLabels(column_headers)

    irow = 0
    for cal_params in calibration_methods:
        if 'noise_response' in cal_params:
            ctrl_err, ctrl_err_sr, ctrl_mae = calc_error(wn_signal, cal_params['noise_response'], frange)
            cal_params['MAE'] = ctrl_mae
            cal_params['NMSE'] = ctrl_err
            cal_params['RMSE'] = ctrl_err_sr
            for icol, col in enumerate(column_headers[:-1]):
                item = QtGui.QTableWidgetItem(str(cal_params[col]))
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
                item = QtGui.QTableWidgetItem(str(cal_params[col]))
                table.setItem(irow, icol, item)
            item = QtGui.QTableWidgetItem('chirp')
            table.setItem(irow, icol+1, item)
            irow +=1

    table.setSortingEnabled(True)
    table.show()
    sys.exit(app.exec_())