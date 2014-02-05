from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import scipy.io.wavfile as wv
from matplotlib.mlab import specgram

import spikeylab.tools.audiotools as audiotools

class SpecWidget(QtGui.QWidget):
    specgram_args = {u'nfft':512, u'window':u'hanning', u'overlap':90}
    cmap = 'jet'
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)

        fig = Figure()
        self.canvas = FigureCanvas(fig)
        self.canvas.setParent(self)

        self.ax = fig.add_subplot(1,1,1)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.setWindowTitle("Spectrogram")

        self.setLayout(vbox)

    def update_data(self, signal, fs):
        spec, f, bins, fs = audiotools.spectrogram((fs, signal), **self.specgram_args)
        self.update_image(spec, bins, f)

    def update_image(self, imgdata, xaxis=None, yaxis=None):
        imgdata = np.flipud(imgdata)
        extent = 0, np.amax(xaxis), yaxis[0], yaxis[-1]
        self.img = self.ax.imshow(imgdata, cmap=self.cmap, extent=extent)
        self.ax.axis('tight')
        self.canvas.draw()

    def from_file(self, fname):
        spec, f, bins, dur = audiotools.spectrogram(fname, **self.specgram_args)

        self.update_image(spec, bins, f)
        return dur

    def set_spec_args(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'colormap':
                self.img.set_cmap(value)
                self.cmap = cmap
            else:
                self.specgram_args[key] = value

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
