import sys
import numpy as np

from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from spikeylab.plotting.custom_plots import TraceWidget, FFTWidget, SpecWidget

from PyQt4 import QtGui, QtCore

class ProtocolDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.fft_plot = FFTWidget(self)
        self.spiketrace_plot = TraceWidget(self)
        self.spec_plot = SpecWidget(self)

        print self.spec_plot.traits.plot.range2d.x_range.default_state, self.spec_plot.traits.plot.range2d.x_range.low_setting
        # self.spec_plot.traits.plot.range2d.x_range = self.spiketrace_plot.traits.trace_plot.range2d.x_range
        # self.spiketrace_plot.traits.trace_plot.components[0].index_mapper.range = self.spec_plot.traits.plot.components[0].index_mapper.range.x_range

        # self.signal_plot.setMinimumHeight(100)
        self.spec_plot.setMinimumHeight(100)
        self.spiketrace_plot.setMinimumWidth(100)
        self.spiketrace_plot.setMinimumHeight(100)
        self.fft_plot.setMinimumWidth(100)
        self.fft_plot.setMinimumHeight(100)

        splittersw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitternw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterse = QtGui.QSplitter(QtCore.Qt.Horizontal)

        # splitternw.addWidget(self.spec_plot)
        # splitternw.addWidget(self.signal_plot)
        # splittersw.addWidget(splitternw)
        splittersw.addWidget(self.spec_plot)
        splittersw.addWidget(self.spiketrace_plot)
        splitterse.addWidget(splittersw)
        splitterse.addWidget(self.fft_plot)

        # set inital sizes
        # splitternw.setSizes([100])
        splittersw.setSizes([100,500])
        splitterse.setSizes([500,100])

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitterse)
        self.setLayout(layout)
        # self.setGeometry(0,0,500,500)

    def update_spec(self, *args, **kwargs):
        self.spec_plot.update_data(*args, **kwargs)

    def update_fft(self, *args, **kwargs):
        self.fft_plot.update_data(*args, **kwargs)

    def update_spiketrace(self, xdata, ydata):
        # self.spiketrace_plot.update_data(*args, **kwargs)
        self.spiketrace_plot.update_data(xdata, datakey='times', axeskey='response')
        self.spiketrace_plot.update_data(ydata, datakey='response', axeskey='response')

    def clear_raster(self):
        self.spiketrace_plot.clear_data("response", "spikes")
        self.spiketrace_plot.clear_data("response", "bins")

    def add_raster_points(self, xdata, repnum):
        """Add a list (or numpy array) of points to raster plot, 
           in any order.
           xdata: bin centers
           ydata: rep number """
        ydata = np.ones_like(xdata)*repnum
        self.spiketrace_plot.append_data(xdata, "response", 'bins')
        self.spiketrace_plot.append_data(ydata, "response", 'spikes')

    def update_signal(self, xdata, ydata):
        # self.signal_plot.update_data(*args, **kwargs)
        self.spiketrace_plot.update_data(xdata, datakey='times', axeskey='stim')
        self.spiketrace_plot.update_data(ydata, datakey='signal', axeskey='stim')

    def set_xlimits(self, lims):
        # print self.spec_plot.traits.plot.range2d.x_range.low, self.spec_plot.traits.plot.range2d.x_range.high

        self.spiketrace_plot.set_xlim(lims)
        self.spec_plot.set_xlim(lims)

    def set_nreps(self, nreps):
        self.spiketrace_plot.set_nreps(nreps)

    def sizeHint(self):
        return QtCore.QSize(500,300)

    # def resizeEvent(self,event):
    #     sz = event.size()
    #     self.item.setGeometry(QtCore.QRectF(0,0,sz.width(), sz.height()))

if __name__ == "__main__":
    import random, time, os
    import numpy as np
    import spikeylab.tools.audiotools as audiotools
    import scipy.io.wavfile as wv
    from scipy.io import loadmat

    app = QtGui.QApplication(sys.argv)
    plot = ProtocolDisplay()
    plot.resize(800, 400)
    plot.show()

    sylpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "sample_syl.wav")
    spec, f, bins, fs = audiotools.spectrogram(sylpath)

    plot.update_spec(spec, xaxis=bins, yaxis=f)

    sr, wavdata = wv.read(sylpath)
    freqs, fft = audiotools.calc_spectrum(wavdata,sr)

    # stim_times = np.arange(0,len(wavdata),1/float(len(wavdata)))
    stim_times = np.linspace(0,float(len(wavdata))/sr, len(wavdata))


    marr = loadmat(os.path.join(os.path.abspath(os.path.dirname(__file__)),"singlesweep.mat"), squeeze_me=True)
    resp = abs(marr['sweep'])
    acq_rate = 50000

    resp_times = np.linspace(0,float(len(resp))/acq_rate, len(resp))

    # x = np.arange(len(wavdata))
    # y = random.randint(0,10) * np.sin(x)

    plot.update_signal(stim_times, wavdata)
    plot.update_spiketrace(resp_times,resp)
    # for i in range(10):
    #     y = random.randint(0,10) * np.sin(x)
    #     plot.update_fft(x,y)
    #     time.sleep(0.2)
    #     QtGui.QApplication.processEvents()
    plot.update_fft(freqs,fft)

    nbins=20
    bin_centers = np.linspace(0,float(len(resp))/acq_rate, nbins)
    dummy_data = np.ones((nbins/2,))
    dummy_bins = bin_centers[0:-1:2]
    plot.add_raster_points(dummy_bins, dummy_data)
    dummy_data = np.ones(((nbins/2)-1,))*2
    dummy_bins = bin_centers[1:-2:2]
    plot.add_raster_points(dummy_bins, dummy_data)
    dummy_data = np.ones(((nbins/2)-1,))*3
    dummy_bins = bin_centers[1:-2:2]
    plot.add_raster_points(dummy_bins, dummy_data)

    print 'spec range', plot.spec_plot.traits.plot.range2d.x_range
    print 'spiketrace range', plot.spiketrace_plot.traits.trace_plot.range2d.x_range

    # coerce x ranges to match
    plot.set_xlimits([0, resp_times[-1]])

    sys.exit(app.exec_())