import sys
import numpy as np

from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from spikeylab.plotting.pyqtgraph_widgets import TraceWidget, SpecWidget, FFTWidget

from PyQt4 import QtGui, QtCore

class ProtocolDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.fft_plot = FFTWidget(self)
        self.spiketrace_plot = TraceWidget(self)
        self.spec_plot = SpecWidget(self)

        self.fft_plot.setToolTip('Stimulus Spectrum')
        self.spiketrace_plot.setToolTip('Spike Trace')
        self.spec_plot.setToolTip('Stimulus Spectrogram')

        self.spec_plot.setXLink(self.spiketrace_plot)
        self.spec_plot.setMinimumHeight(100)
        self.spiketrace_plot.setMinimumWidth(100)
        self.spiketrace_plot.setMinimumHeight(100)
        self.fft_plot.setMinimumWidth(100)
        self.fft_plot.setMinimumHeight(100)

        splittersw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitternw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterse = QtGui.QSplitter(QtCore.Qt.Horizontal)

        splittersw.addWidget(self.spec_plot)
        splittersw.addWidget(self.spiketrace_plot)
        splitterse.addWidget(splittersw)
        splitterse.addWidget(self.fft_plot)

        # set inital sizes
        splittersw.setSizes([100,500])
        splitterse.setSizes([500,100])

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitterse)
        self.setLayout(layout)

        #relay threshold signal
        self.threshold_updated = self.spiketrace_plot.threshold_updated
        self.colormap_changed = self.spec_plot.colormap_changed

        # for the purposes of splitter not updating contents...
        self.splittersw = splittersw
        self.badbadbad = 0

    def update_spec(self, *args, **kwargs):
        if args[0] == None:
            self.spec_plot.clear_img()
        else:
            self.spec_plot.from_file(*args, **kwargs)

    def show_spec(self, fname):
        """ Draw image if none present """
        if not self.spec_plot.has_img() and fname is not None:
            self.spec_plot.from_file(fname)

    def set_spec_args(self, *args, **kwargs):
        self.spec_plot.set_spec_args(*args, **kwargs)

    def update_fft(self, *args, **kwargs):
        self.fft_plot.update_data(*args, **kwargs)

    def update_spiketrace(self, xdata, ydata):
        self.spiketrace_plot.update_data(axeskey='response', x=xdata, y=ydata)

    def clear_raster(self):
        self.spiketrace_plot.clear_data('raster')

    def add_raster_points(self, xdata, repnum):
        """Add a list (or numpy array) of points to raster plot, 
           in any order.
           xdata: bin centers
           ydata: rep number """
        ydata = np.ones_like(xdata)*repnum
        self.spiketrace_plot.append_data('raster', xdata, ydata)

    def update_signal(self, xdata, ydata):
        self.spiketrace_plot.update_data(axeskey='stim', x=xdata, y=ydata)

    def set_xlimits(self, lims):
        self.spiketrace_plot.set_xlim(lims)
        # ridiculous...
        sizes = self.splittersw.sizes()
        if self.badbadbad:
            sizes[0] +=1
            sizes[1] -=1
        else:
            sizes[0] -=1
            sizes[1] +=1
        self.badbadbad = not self.badbadbad
        self.splittersw.setSizes(sizes)

    def set_nreps(self, nreps):
        self.spiketrace_plot.set_nreps(nreps)

    def sizeHint(self):
        return QtCore.QSize(500,300)

    def set_tscale(self, scale):
        self.spiketrace_plot.set_tscale(scale)
        self.spec_plot.set_tscale(scale)

    def set_fscale(self, scale):
        self.fft_plot.set_fscale(scale)
        self.spec_plot.set_fscale(scale)

if __name__ == "__main__":
    import random, time, os
    import numpy as np
    import spikeylab.tools.audiotools as audiotools
    import scipy.io.wavfile as wv
    import test.sample as sample
    from scipy.io import loadmat

    app = QtGui.QApplication(sys.argv)
    plot = ProtocolDisplay()
    plot.resize(800, 400)
    plot.show()

    sylpath = sample.samplewav()
    spec, f, bins, fs = audiotools.spectrogram(sylpath)

    # plot.update_spec(spec, xaxis=bins, yaxis=f)
    plot.update_spec(sylpath)

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


    # coerce x ranges to match
    plot.set_xlimits([0, resp_times[-1]])

    plot.set_tscale(0.001)
    plot.set_fscale(1000)

    sys.exit(app.exec_())