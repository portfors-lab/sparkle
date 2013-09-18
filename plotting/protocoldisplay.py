import sys

from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"
from enthought.chaco.api import GridPlotContainer

from audiolab.plotting.chacoplots import ImagePlotter, Plotter, DataPlotWidget, ImageWidget, TraceWidget

from PyQt4 import QtGui, QtCore

class ProtocolDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.spec_plot = ImageWidget(self)
        # self.fft_plot = Plotter(self, 1, rotation = -90)
        self.fft_plot = DataPlotWidget(orientation='v')
        self.spiketrace_plot = TraceWidget(self)
        # self.spiketrace_plot = DataPlotWidget(self)
        # self.signal_plot = DataPlotWidget(self)

        # container = GridPlotContainer(shape=(3,2))
        # container.insert(0, self.spec_plot)
        # container.insert(2, self.signal_plot)
        # container.insert(4, self.spiketrace_plot)
        # container.insert(5, self.fft_plot)

        # self.signal_plot.setMinimumHeight(100)
        self.spec_plot.setMinimumHeight(100)
        self.spiketrace_plot.setMinimumWidth(100)
        self.spiketrace_plot.setMinimumHeight(100)
        self.fft_plot.setMinimumWidth(100)
        self.fft_plot.setMinimumHeight(100)

        # layout = QtGui.QGridLayout()
        # # layout.setSpacing(10)
        # layout.addWidget(self.spec_plot.widget, 0, 0)
        # layout.addWidget(self.signal_plot.widget, 1, 0)
        # layout.addWidget(self.spiketrace_plot.widget, 2, 0)
        # layout.addWidget(self.fft_plot.widget, 2, 1)

        splittersw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitternw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterse = QtGui.QSplitter(QtCore.Qt.Horizontal)

        splitternw.addWidget(self.spec_plot)
        # splitternw.addWidget(self.signal_plot)
        splittersw.addWidget(splitternw)
        splitternw.addWidget(self.spiketrace_plot)
        splitterse.addWidget(splitternw)
        # splitterse.addWidget(RotatableView(self.fft_plot))
        splitterse.addWidget(self.fft_plot)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(splitterse)
        self.setLayout(layout)
        # self.setGeometry(0,0,500,500)

    def update_spec(self, *args, **kwargs):
        self.spec_plot.update_data(*args, **kwargs)

    def update_fft(self, *args, **kwargs):
        self.fft_plot.update_data(*args, **kwargs)

    def update_spiketrace(self, *args, **kwargs):
        self.spiketrace_plot.update_data(*args, **kwargs)

    def update_signal(self, *args, **kwargs):
        # self.signal_plot.update_data(*args, **kwargs)
        self.spiketrace_plot.update_data(*args, **kwargs)

    def set_xlimits(self, lims):
        self.spec_plot.set_xlim(lims)
        self.signal_plot.set_xlim(lims)
        self.spiketrace_plot.set_xlim(lims)

    def sizeHint(self):
        return QtCore.QSize(500,300)

    def resizeEvent(self,event):
        sz = event.size()
        self.item.setGeometry(QtCore.QRectF(0,0,sz.width(), sz.height()))

if __name__ == "__main__":
    import random, time, os
    import numpy as np
    import audiolab.tools.audiotools as audiotools
    import scipy.io.wavfile as wv


    app = QtGui.QApplication(sys.argv)
    plot = ProtocolDisplay()
    plot.resize(800, 400)
    plot.show()

    sylpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "sample_syl.wav")
    spec, f, bins, fs = audiotools.spectrogram(sylpath)
    plot.update_spec(spec, xaxis=bins, yaxis=f)


    sr, wavdata = wv.read(sylpath)
    freqs, fft = audiotools.calc_spectrum(wavdata,sr)

    print len(wavdata)
    # stim_times = np.arange(0,len(wavdata),1/float(len(wavdata)))
    stim_times = np.linspace(0,len(wavdata)*sr, len(wavdata))

    x = np.arange(len(wavdata))
    y = random.randint(0,10) * np.sin(x)
    # plot.update_signal(x,y)
    # plot.update_spiketrace(x,y)
    plot.update_signal(stim_times, datakey='times', axeskey='stim')
    plot.update_signal(wavdata, datakey='signal', axeskey='stim')
    plot.update_spiketrace(stim_times, datakey='times', axeskey='response')
    plot.update_spiketrace(y, datakey='response', axeskey='response')
    for i in range(10):
        y = random.randint(0,10) * np.sin(x)
        plot.update_fft(x,y)
        time.sleep(0.2)
        QtGui.QApplication.processEvents()
    plot.update_fft(freqs,fft) 

    sys.exit(app.exec_())