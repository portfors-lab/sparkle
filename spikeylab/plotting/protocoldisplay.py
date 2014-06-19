import sys
import numpy as np

from spikeylab.plotting.pyqtgraph_widgets import TraceWidget, SpecWidget, FFTWidget

from PyQt4 import QtGui, QtCore

class ProtocolDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.fftPlot = FFTWidget(self, rotation=-90)
        self.spiketracePlot = TraceWidget(self)
        self.specPlot = SpecWidget(self)

        self.fftPlot.setToolTip('Stimulus Spectrum')
        self.spiketracePlot.setToolTip('Spike Trace')
        self.specPlot.setToolTip('Stimulus Spectrogram')

        # custom behaviour for spec view all option
        vb = self.specPlot.getViewBox()
        vb.menu.viewAll.triggered.disconnect()
        vb.menu.viewAll.triggered.connect(self.specAutoRange)
        # self.fftPlot.set_title("Stimulus FFT")
        # self.spiketracePlot.set_title("Response Trace")
        # self.specPlot.set_title("Stimulus Spectrogram")

        self.specPlot.setXLink(self.spiketracePlot)
        self.specPlot.setMinimumHeight(100)
        self.spiketracePlot.setMinimumWidth(100)
        self.spiketracePlot.setMinimumHeight(100)
        self.fftPlot.setMinimumWidth(100)
        self.fftPlot.setMinimumHeight(100)

        splittersw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterse = QtGui.QSplitter(QtCore.Qt.Horizontal)

        splittersw.addWidget(self.specPlot)
        splittersw.addWidget(self.spiketracePlot)
        splitterse.addWidget(splittersw)
        splitterse.addWidget(self.fftPlot)

        # set inital sizes
        splittersw.setSizes([100,500])
        splitterse.setSizes([500,100])

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitterse)
        self.setLayout(layout)

        #relay threshold signal
        self.thresholdUpdated = self.spiketracePlot.thresholdUpdated
        self.colormapChanged = self.specPlot.colormapChanged

        # for the purposes of splitter not updating contents...
        self.splittersw = splittersw
        self.badbadbad = 0

    def updateSpec(self, *args, **kwargs):
        if args[0] == None:
            self.specPlot.clearImg()
        elif isinstance(args[0], basestring):
            self.specPlot.fromFile(*args, **kwargs)
        else:
            self.specPlot.updateData(*args,**kwargs)
            
    def showSpec(self, fname):
        """ Draw image if none present """
        if not self.specPlot.has_img() and fname is not None:
            self.specPlot.fromFile(fname)

    def setSpecArgs(self, *args, **kwargs):
        self.specPlot.setSpecArgs(*args, **kwargs)

    def updateFft(self, *args, **kwargs):
        self.fftPlot.updateData(*args, **kwargs)

    def updateSpiketrace(self, xdata, ydata):
        self.spiketracePlot.updateData(axeskey='response', x=xdata, y=ydata)

    def clearRaster(self):
        self.spiketracePlot.clearData('raster')

    def addRasterPoints(self, xdata, repnum):
        """Add a list (or numpy array) of points to raster plot, 
           in any order.
           xdata: bin centers
           ydata: rep number """
        ydata = np.ones_like(xdata)*repnum
        self.spiketracePlot.appendData('raster', xdata, ydata)

    def updateSignal(self, xdata, ydata):
        self.spiketracePlot.updateData(axeskey='stim', x=xdata, y=ydata)

    def setXlimits(self, lims):
        self.spiketracePlot.setXlim(lims)
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

    def setNreps(self, nreps):
        self.spiketracePlot.setNreps(nreps)

    def sizeHint(self):
        return QtCore.QSize(500,300)

    def setTscale(self, scale):
        self.spiketracePlot.setTscale(scale)
        self.specPlot.setTscale(scale)

    def setFscale(self, scale):
        self.fftPlot.setFscale(scale)
        self.specPlot.setFscale(scale)

    def specAutoRange(self):
        trace_range = self.spiketracePlot.viewRange()[0]
        vb = self.specPlot.getViewBox()
        vb.autoRange(padding=0)
        self.specPlot.setXlim(trace_range)


if __name__ == "__main__":
    import random, time, os
    import numpy as np
    import spikeylab.tools.audiotools as audiotools
    import scipy.acq.wavfile as wv
    import test.sample as sample
    from scipy.io import loadmat

    app = QtGui.QApplication(sys.argv)
    plot = ProtocolDisplay()
    plot.resize(800, 400)
    plot.show()

    sylpath = sample.samplewav()
    spec, f, bins, fs = audiotools.spectrogram(sylpath)

    # plot.updateSpec(spec, xaxis=bins, yaxis=f)
    plot.updateSpec(sylpath)

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

    plot.updateSignal(stim_times, wavdata)
    plot.updateSpiketrace(resp_times,resp)
    # for i in range(10):
    #     y = random.randint(0,10) * np.sin(x)
    #     plot.updateFft(x,y)
    #     time.sleep(0.2)
    #     QtGui.QApplication.processEvents()
    plot.updateFft(freqs,fft)

    nbins=20
    bin_centers = np.linspace(0,float(len(resp))/acq_rate, nbins)
    dummy_data = np.ones((nbins/2,))
    dummy_bins = bin_centers[0:-1:2]
    plot.addRasterPoints(dummy_bins, dummy_data)
    dummy_data = np.ones(((nbins/2)-1,))*2
    dummy_bins = bin_centers[1:-2:2]
    plot.addRasterPoints(dummy_bins, dummy_data)
    dummy_data = np.ones(((nbins/2)-1,))*3
    dummy_bins = bin_centers[1:-2:2]
    plot.addRasterPoints(dummy_bins, dummy_data)


    # coerce x ranges to match
    plot.setXlimits([0, resp_times[-1]])

    plot.setTscale(0.001)
    plot.setFscale(1000)

    sys.exit(app.exec_())