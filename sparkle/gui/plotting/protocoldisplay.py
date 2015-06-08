import numpy as np

from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.plotting.pyqtgraph_widgets import FFTWidget, SpecWidget, \
    TraceWidget


class ProtocolDisplay(QtGui.QWidget):
    """Data display intended for use during brain recording"""
    thresholdUpdated = QtCore.Signal(float, str)
    polarityInverted = QtCore.Signal(float, str)
    rasterBoundsUpdated = QtCore.Signal(tuple, str)
    absUpdated = QtCore.Signal(bool, str)
    def __init__(self, response_chan_name='chan0', parent=None):
        super(ProtocolDisplay, self).__init__(parent)

        self.responsePlots = {}
        self.fftPlot = FFTWidget(self, rotation=90)
        spiketracePlot = TraceWidget(self)
        self.responsePlots[response_chan_name] = spiketracePlot
        self.specPlot = SpecWidget(self)

        self.fftPlot.setToolTip('Stimulus Spectrum')
        spiketracePlot.setToolTip('Spike Trace')
        self.specPlot.setToolTip('Stimulus Spectrogram')

        # custom behaviour for spec view all option
        vb = self.specPlot.getViewBox() 
        vb.menu.viewAll.triggered.disconnect()
        vb.menu.viewAll.triggered.connect(self.specAutoRange)
        # self.fftPlot.set_title("Stimulus FFT")
        # spiketracePlot.set_title("Response Trace")
        # self.specPlot.set_title("Stimulus Spectrogram")

        self.specPlot.plotItem.vb.sigXRangeChanged.connect(self.updateXRange)
        spiketracePlot.plotItem.vb.sigXRangeChanged.connect(self.updateXRange)
        self.specPlot.setMinimumHeight(100)
        spiketracePlot.setMinimumWidth(100)
        spiketracePlot.setMinimumHeight(100)
        self.fftPlot.setMinimumWidth(100)
        self.fftPlot.setMinimumHeight(100)

        splittersw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterse = QtGui.QSplitter(QtCore.Qt.Horizontal)

        splittersw.addWidget(self.specPlot)
        splittersw.addWidget(spiketracePlot)
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
        spiketracePlot.thresholdUpdated.connect(self.thresholdUpdated.emit)
        spiketracePlot.polarityInverted.connect(self.polarityInverted.emit)
        spiketracePlot.rasterBoundsUpdated.connect(self.rasterBoundsUpdated.emit)
        spiketracePlot.absUpdated.connect(self.absUpdated.emit)
        self.colormapChanged = self.specPlot.colormapChanged

        # for the purposes of splitter not updating contents...
        self.splittersw = splittersw
        self.badbadbad = 0
        self._ignore_range_signal = False    

    def updateSpec(self, *args, **kwargs):
        """Updates the spectrogram. First argument can be a filename, 
        or a data array. If no arguments are given, clears the spectrograms.

        For other arguments, see: :meth:`SpecWidget.updateData<sparkle.gui.plotting.pyqtgraph_widgets.SpecWidget.updateData>`
        """
        if args[0] is None:
            self.specPlot.clearImg()
        elif isinstance(args[0], basestring):
            self.specPlot.fromFile(*args, **kwargs)
        else:
            self.specPlot.updateData(*args,**kwargs)
            
    def showSpec(self, fname):
        """Draws the spectrogram if it is currently None"""
        if not self.specPlot.hasImg() and fname is not None:
            self.specPlot.fromFile(fname)

    def updateFft(self, *args, **kwargs):
        """Updates the FFT plot with new data

        For arguments, see: :meth:`FFTWidget.updateData<sparkle.gui.plotting.pyqtgraph_widgets.FFTWidget.updateData>`
        """
        self.fftPlot.updateData(*args, **kwargs)

    def addResponsePlot(self, *names):
        for name in names:
            plot = TraceWidget(self)
            plot.setTitle(name)
            plot.plotItem.vb.sigXRangeChanged.connect(self.updateXRange)
            self.splittersw.addWidget(plot)
            plot.thresholdUpdated.connect(self.thresholdUpdated.emit)
            plot.polarityInverted.connect(self.polarityInverted.emit)
            plot.rasterBoundsUpdated.connect(self.rasterBoundsUpdated.emit)
            plot.absUpdated.connect(self.absUpdated.emit)
            self.responsePlots[name] = plot

    def removeResponsePlot(self, *names):
        for name in names:
            if name in self.responsePlots:
                plot = self.responsePlots.pop(name)
                plot.thresholdUpdated.disconnect()
                plot.polarityInverted.disconnect()
                plot.rasterBoundsUpdated.disconnect()
                plot.absUpdated.disconnect()
                plot.plotItem.vb.sigXRangeChanged.disconnect()
                plot.close()
                plot.deleteLater()

    def responseNameList(self):
        return self.responsePlots.keys()

    def responsePlotCount(self):
        return len(self.responsePlots)

    def updateSpiketrace(self, xdata, ydata, plotname=None):
        """Updates the spike trace

        :param xdata: index values
        :type xdata: numpy.ndarray
        :param ydata: values to plot
        :type ydata: numpy.ndarray
        """
        if plotname is None:
            plotname = self.responsePlots.keys()[0]

        if len(ydata.shape) == 1 or ydata.shape[0] == 1:
            self.responsePlots[plotname].updateData(axeskey='response', x=xdata, y=ydata)
        else:
            self.responsePlots[plotname].addTraces(xdata, ydata)

    def clearRaster(self):
        """Clears data from the raster plots"""
        for plot in self.responsePlots.values():
            plot.clearData('raster')

    def addRasterPoints(self, xdata, repnum, plotname=None):
        """Add a list (or numpy array) of points to raster plot, 
        in any order.

        :param xdata: bin centers
        :param ydata: rep number 
        """
        if plotname is None:
            plotname = self.responsePlots.keys()[0]
        ydata = np.ones_like(xdata)*repnum
        self.responsePlots[plotname].appendData('raster', xdata, ydata)

    def updateSignal(self, xdata, ydata, plotname=None):
        """Updates the trace of the outgoing signal

        :param xdata: time points of recording
        :param ydata: brain potential at time points
        """
        if plotname is None:
            plotname = self.responsePlots.keys()[0]
        self.responsePlots[plotname].updateData(axeskey='stim', x=xdata, y=ydata)

    def setXlimits(self, lims):
        """Sets the X axis limits of the trace plot

        :param lims: (min, max) of x axis, in same units as data
        :type lims: (float, float)
        """
        # update all "linked", plots
        self.specPlot.setXlim(lims)
        for plot in self.responsePlots.values():
            plot.setXlim(lims)
        # ridiculous...
        sizes = self.splittersw.sizes()
        if len(sizes) > 1:
            if self.badbadbad:
                sizes[0] +=1
                sizes[1] -=1
            else:
                sizes[0] -=1
                sizes[1] +=1
            self.badbadbad = not self.badbadbad
            self.splittersw.setSizes(sizes)

        self._ignore_range_signal = False

    def updateXRange(self, view, lims):
        if not self._ignore_range_signal:
            # avoid crazy recursion, as we update the other plots
            self._ignore_range_signal = True
            self.setXlimits(lims)

    def setNreps(self, nreps):
        """Sets the number of reps before the raster plot resets"""
        for plot in self.responsePlots.values():
            plot.setNreps(nreps)

    def sizeHint(self):
        """default size?"""
        return QtCore.QSize(500,300)

    def specAutoRange(self):
        """Auto adjusts the visible range of the spectrogram"""
        trace_range = self.responsePlots.values()[0].viewRange()[0]
        vb = self.specPlot.getViewBox()
        vb.autoRange(padding=0)
        self.specPlot.setXlim(trace_range)

    def setAmpConversionFactor(self, scalar):
        for plot in self.responsePlots.values():
            plot.setAmpConversionFactor(scalar)

    def setThreshold(self, thresh, plotname):
        self.responsePlots[plotname].setThreshold(thresh)

    def setRasterBounds(self, bounds, plotname):
        self.responsePlots[plotname].setRasterBounds(bounds)

    def setAbs(self, bounds, plotname):
        self.responsePlots[plotname].setAbs(bounds)


if __name__ == "__main__":
    import random, time, os, sys
    import numpy as np
    import sparkle.tools.audiotools as audiotools
    import scipy.io.wavfile as wv
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

    fs, wavdata = wv.read(sylpath)
    freqs, fft = audiotools.calc_spectrum(wavdata,fs)

    # stim_times = np.arange(0,len(wavdata),1/float(len(wavdata)))
    stim_times = np.linspace(0,float(len(wavdata))/fs, len(wavdata))


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
