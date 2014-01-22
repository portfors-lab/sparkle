from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import scipy.io.wavfile as wv
from matplotlib.mlab import specgram

class SpecWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)

        fig = Figure()
        self.canvas = FigureCanvas(fig)
        self.canvas.setParent(self)

        self.ax = fig.add_subplot(1,1,1)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)

    def update_data(self, imgdata, xaxis=None, yaxis=None):
        self.ax.imshow(imgdata)
        self.canvas.draw()

    def update_file(self, fname):
        nfft=512
        try:
            sr, wavdata = wv.read(fname)
        except:
            print u"Problem reading wav file"
            raise
        wavdata = wavdata.astype(float)
        self.ax.clear()
        data = self.ax.specgram(wavdata, NFFT=nfft, Fs=sr, noverlap=int(nfft*0.9),
                                pad_to=nfft*2)
        self.ax.axis('tight')
        self.canvas.draw()
        return float(len(wavdata))/sr

if __name__ == '__main__':
    import sys
    from spikeylab.tools.audiotools import spectrogram

    app  = QtGui.QApplication(sys.argv)

    fname = r'C:\Users\amy.boyle\Dropbox\daqstuff\M1_FD024\M1_FD024_syl_12.wav'
    spec, f, bins, fs = spectrogram(fname)
    specplot = SpecWidget()
    specplot.update_data(spec)
    specplot.show()
    sys.exit(app.exec_())
