from PyQt4 import QtCore, QtGui
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import scipy.io.wavfile as wv
from matplotlib.mlab import specgram

import spikeylab.tools.audiotools as audiotools

class SpecWidget(QtGui.QWidget):
    specgram_args = {u'nfft':512, u'window':u'hanning', u'overlap':90}
    img_args = {'cmap':'jet'}
    fscale = 1000
    tscale = 0.001
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)

        fig = Figure()
        self.canvas = FigureCanvas(fig)
        fig.patch.set_color('0.95')

        self.canvas.setParent(self)

        self.ax = fig.add_subplot(1,1,1)
        self.position = [50.0, 10.0]
        self.img = None

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        # vbox.setContentsMargins(0,0,0,0)

        self.setWindowTitle("Spectrogram")

        self.setLayout(vbox)

    def update_data(self, signal, fs):
        spec, f, bins, fs = audiotools.spectrogram((fs, signal), **self.specgram_args)
        self.update_image(spec, bins, f)

    def update_image(self, imgdata, xaxis=None, yaxis=None):
        imgdata = np.flipud(imgdata)
        extent = 0, np.amax(xaxis), yaxis[0], yaxis[-1]
        self.img = self.ax.imshow(imgdata, cmap=self.img_args['cmap'], extent=extent)
        self.ax.axis('tight')
        self.canvas.draw()

    def from_file(self, fname):
        spec, f, bins, dur = audiotools.spectrogram(fname, **self.specgram_args)

        self.update_image(spec, bins, f)
        return dur

    def set_spec_args(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'colormap':
                self.img_args['cmap'] = value
                if self.img is not None:
                    self.img.set_cmap(value)
                    self.canvas.draw()
            else:
                self.specgram_args[key] = value

    def set_xlim(self, lims):
        self.ax.set_xlim(*lims)
        self.canvas.draw()

    def resizeEvent(self, event):
        width = event.size().width()
        height = event.size().height()
        relx = self.position[0]/width
        rely = self.position[1]/height
        # print 'width', width, 'height', height, 'relxy', relx, rely
        self.ax.set_position([relx, rely, 1.0-relx, 1.0-rely])

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
