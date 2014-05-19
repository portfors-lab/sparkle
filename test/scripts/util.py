import sys, time
import numpy as np

from PyQt4 import QtGui, QtCore

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


def record(player, sig, fs, atten=0):
    nreps = 3
    reps = []
    player.set_stim(sig, fs, atten)
    player.start()
    for irep in range(nreps):
        response = player.run()
        reps.append(response)
        player.reset()

    player.stop()
    return np.mean(reps, axis=0)

