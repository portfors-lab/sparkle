import time

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import threading

from spikeylab.plotting.viewbox import SpikeyViewBox
from spikeylab.plotting.raster_bounds_dlg import RasterBoundsDialog
import spikeylab.tools.audiotools as audiotools

STIM_HEIGHT = 0.05

## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(useWeave=False)

class BasePlot(pg.PlotWidget):
    """Abstract class meant to be subclassed by other plot types.

    Handles some common user interaction to be the same across plots
    """
    def __init__(self, parent=None):
        super(BasePlot, self).__init__(parent, viewBox=SpikeyViewBox())

        # print 'scene', self.scene().contextMenu[0].text()
        # # self.scene().contextMenu = []
        # print '-'*20
        # for act in self.getPlotItem().vb.menu.actions():
        #     if act.text() != 'View All':
        #         print 'removing', act.text()
        #         self.getPlotItem().vb.menu.removeAction(act)
        # print '-'*20

        for act in self.getPlotItem().ctrlMenu.actions():
            # print act.text()
            if act.text() != 'Grid':
                self.getPlotItem().ctrlMenu.removeAction(act)
                
        self.setMouseEnabled(x=False,y=True)

    def setTscale(self, scale):
        pass

    def setFscale(self, scale):
        pass

    def setXlim(self, lim):
        self.setXRange(*lim, padding=0)

    def setYlim(self, lim):
        self.setYRange(*lim)

    def setTitle(self, title):
        self.getPlotItem().setTitle(title)

    def getLabel(self, key):
        axisItem = self.getPlotItem().axes[key]['item']
        return axisItem.label.toPlainText()

class TraceWidget(BasePlot):
    """Main plot object for experimental data

    Includes : recording electrode trace
               stimulus signal
               spike raster
    """
    nreps = 20
    rasterYmin = 0.5
    rasterYmax = 1
    rasterYslots = np.linspace(rasterYmin, rasterYmax, nreps)
    thresholdUpdated = QtCore.pyqtSignal(float)
    def __init__(self, parent=None):
        super(TraceWidget, self).__init__(parent)

        self.tracePlot = self.plot(pen='k')
        self.rasterPlot = self.plot(pen=None, symbol='s', symbolPen=None, symbolSize=4, symbolBrush='k')
        self.stimPlot = self.plot(pen='b')
        self.stimPlot.curve.setToolTip("Stimulus Signal")
        self.tracePlot.curve.setToolTip("Spike Trace")

        self.sigRangeChanged.connect(self.rangeChange)

        self.disableAutoRange()

        rasterBoundsAction = QtGui.QAction("Edit raster bounds", None)
        self.scene().contextMenu.append(rasterBoundsAction) #should use function for this?
        rasterBoundsAction.triggered.connect(self.askRasterBounds)

        self.threshLine = pg.InfiniteLine(pos=0.5, angle=0, pen='r', movable=True)
        self.addItem(self.threshLine)
        self.threshLine.sigPositionChangeFinished.connect(self.update_thresh)
        self.setLabel('left', 'Potential', units='V')
        self.setLabel('bottom', 'Time', units='s')

    def updateData(self, axeskey, x, y):
        """Replaces the currently displayed data

        :param axeskey: name of data plot to update. Valid options are 'stim' or 'response'
        :type axeskey: str
        :param x: index values associated with y to plot
        :type x: numpy.ndarray
        :param y: values to plot at x
        :type y: numpy.ndarray
        """
        if axeskey == 'stim':
            self.stimPlot.setData(x,y)
            # call manually to ajust placement of signal
            ranges = self.viewRange()
            self.rangeChange(self, ranges)
        if axeskey == 'response':
            self.tracePlot.setData(x,y)

    def appendData(self, axeskey, bins, ypoints):
        """Appends data to existing plotted data

        :param axeskey: name of data plot to update. Valid options are 'stim' or 'response'
        :type axeskey: str
        :param bins: bins to plot a point for
        :type bin: numpy.ndarray
        :param ypoints: iteration number of raster, *should* match bins dimension, but really takes the first value in array for iteration number and plot row at proper place for included bins
        :type ypoints: numpy.ndarray
        """
        if axeskey == 'raster':
            x, y = self.rasterPlot.getData()
            # don't plot overlapping points
            bins = np.unique(bins)
            # adjust repetition number to response scale
            ypoints = np.ones_like(bins)*self.rasterYslots[ypoints[0]]
            x = np.append(x, bins)
            y = np.append(y, ypoints)
            self.rasterPlot.setData(x, y)

    def clearData(self, axeskey):
        """Clears the raster plot"""
        self.rasterPlot.clear()

    def getThreshold(self):
        """Current Threshold value

        :returns: float -- y values of the threshold line
        """
        y = self.threshLine.value()
        return y

    def setThreshold(self, threshold):
        """Sets the current threshold

        :param threshold: the y value to set the threshold line at
        :type threshold: float
        """
        self.threshLine.setValue(threshold) 

    def setNreps(self, nreps):
        """Sets the number of reps user by raster plot to determine where to place data points

        :param nreps: number of iterations before the raster will be cleared
        :type nreps: int
        """
        self.nreps = nreps
        self.rasterYslots = np.linspace(self.rasterYmin, self.rasterYmax, self.nreps)

    def setRasterBounds(self,lims):
        """Sets the raster plot y-axis bounds, where in the plot the raster will appear between

        :param lims: the (min, max) y-values for the raster plot to be placed between
        :type lims: (float, float)
        """
        self.rasterYmin = lims[0]
        self.rasterYmax = lims[1]
        self.rasterYslots = np.linspace(self.rasterYmin, self.rasterYmax, self.nreps)

    def askRasterBounds(self):
        """Prompt the user to provide the raster bounds with a dialog. Saves the bounds to be applied to the plot"""
        dlg = RasterBoundsDialog(bounds= (self.rasterYmin, self.rasterYmax))
        if dlg.exec_():
            bounds = dlg.values()
            self.setRasterBounds(bounds)

    def getRasterBounds(self):
        """Current raster y-axis plot limits

        :retruns: (float, float) -- (min, max) of raster plot bounds
        """
        return (self.rasterYmin, self.rasterYmax)

    def rangeChange(self, pw, ranges):
        if hasattr(ranges, '__iter__'):
            # adjust the stim signal so that it falls in the correct range
            stim_x, stim_y = self.stimPlot.getData()
            if stim_y is not None:
                yrange_size = ranges[1][1] - ranges[1][0]
                stim_height = yrange_size*STIM_HEIGHT
                # take it to 0
                stim_y = stim_y - np.amin(stim_y)
                # normalize
                if np.amax(stim_y) != 0:
                    stim_y = stim_y/np.amax(stim_y)
                # scale for new size
                stim_y = stim_y*stim_height
                # raise to right place in plot
                stim_y = stim_y + (ranges[1][1] - (stim_height*1.1 + (stim_height*0.2)))
                self.stimPlot.setData(stim_x, stim_y)

    def update_thresh(self):
        """Emits a Qt signal thresholdUpdated with the current threshold value"""
        self.thresholdUpdated.emit(self.threshLine.value())


def _doSpectrogram(signal, *args, **kwargs):
    spec, f, bins, dur = audiotools.spectrogram(*args, **kwargs)
    signal.emit(spec, bins, f)

class SpecWidget(BasePlot):
    """Widget for displaying a spectrogram"""
    specgramArgs = {u'nfft':512, u'window':u'hanning', u'overlap':90}
    imgArgs = {'lut':None, 'state':None, 'levels':None}
    resetImageScale = True
    imgScale = (1.,1.)
    colormapChanged = QtCore.pyqtSignal(object)
    spec_done = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    def __init__(self, parent=None):
        super(SpecWidget, self).__init__(parent)

        self.img = pg.ImageItem()
        self.addItem(self.img)
        self.imageArray = np.array([[0]])

        cmapAction = QtGui.QAction("Edit colormap", None)
        self.scene().contextMenu.append(cmapAction) #should use function for this?
        cmapAction.triggered.connect(self.editColormap)

        self.setLabel('bottom', 'Time', units='s')
        self.setLabel('left', 'Frequency', units='Hz')

        self.spec_done.connect(self.updateImage)

    def fromFile(self, fname):
        """Displays a spectrogram of an audio file. Supported formats see :mod:`spikeylab.audiolab`

        :param fname: file path of the audiofile to display
        :type fname: str
        :returns: float -- duration of audio recording (seconds)
        """
        spec, f, bins, dur = audiotools.spectrogram(fname, **self.specgramArgs)
        self.updateImage(spec, bins, f)
        return dur

    def updateImage(self, imgdata, xaxis=None, yaxis=None):
        """Updates the Widget image directly

        :param imgdata: array of image data to displayed see :func:`pyqtgraph.ImageItem.setImage`
        :type imgdata: numpy.ndarray
        :param xaxis: x-axis values, length should match dimension 1 of imgdata
        :param yaxis: y-axis values, length should match dimension 0 of imgdata
        """
        imgdata = imgdata.T
        self.img.setImage(imgdata)
        if xaxis is not None and yaxis is not None:
            xscale = 1.0/(imgdata.shape[0]/xaxis[-1])
            yscale = 1.0/(imgdata.shape[1]/yaxis[-1])
            self.resetScale()        
            self.img.scale(xscale, yscale)
            self.imgScale = (xscale, yscale)
        self.imageArray = np.fliplr(imgdata)
        self.updateColormap()

    def resetScale(self):
        """Resets the scale on this image"""
        print 'RESET SCALCE EXLABORATE DOCSTRING'
        self.img.scale(1./self.imgScale[0], 1./self.imgScale[1])
        self.imgScale = (1.,1.)

    def updateData(self, signal, fs):
        """Displays a spectrogram of the provided signal

        :param signal: 1-D signal of audio
        :type signal: numpy.ndarray
        :param fs: samplerate of signal
        :type fs: int
        """
        # use a separate thread to calculate spectrogram so UI doesn't lag
        t = threading.Thread(target=_doSpectrogram, args=(self.spec_done, (fs, signal),), kwargs=self.specgramArgs)
        t.start()

    def setSpecArgs(self, **kwargs):
        """Sets optional arguments for the spectrogram appearance.

        Available options:
        :param nfft: size of FFT window to use
        :type nfft: int
        :param overlap: percent overlap of window
        :type overlap: number
        :param window: Type of window to use, choices are hanning, hamming, blackman, bartlett or none (rectangular)
        :type window: string
        :param colormap: see :mod:`some pyqtgraph class`
        """
        for key, value in kwargs.items():
            if key == 'colormap':
                self.imgArgs['lut'] = value['lut']
                self.imgArgs['levels'] = value['levels']
                self.imgArgs['state'] = value['state']
                self.updateColormap()
            else:
                self.specgramArgs[key] = value

    def clearImg(self):
        """Clears the current image"""
        self.img.setImage(np.array([[0]]))
        self.img.image = None

    def hasImg(self):
        """Whether an image is currently displayed"""
        return self.img.image is not None

    def editColormap(self):
        """Prompts the user with a dialog to change colormap"""
        self.editor = pg.ImageView()
        # remove the ROI and Norm buttons
        self.editor.ui.roiBtn.setVisible(False)
        self.editor.ui.normBtn.setVisible(False)
        self.editor.setImage(self.imageArray)
        if self.imgArgs['state'] is not None:
            self.editor.getHistogramWidget().item.gradient.restoreState(self.imgArgs['state'])
            self.editor.getHistogramWidget().item.setLevels(*self.imgArgs['levels'])
        
        self.editor.closeEvent = self._editor_close
        self.editor.show()

    def _editor_close(self, event):
        lut = self.editor.getHistogramWidget().item.getLookupTable(n=512, alpha=True)
        state = self.editor.getHistogramWidget().item.gradient.saveState()
        levels = self.editor.getHistogramWidget().item.getLevels()
        self.img.setLookupTable(lut)
        self.img.setLevels(levels)
        self.imgArgs['lut'] = lut
        self.imgArgs['state'] = state
        self.imgArgs['levels'] = levels
        self.colormapChanged.emit(self.imgArgs)

    def updateColormap(self):
        """Updates the currently colormap accoring to stored settings"""
        if self.imgArgs['lut'] is not None:
            self.img.setLookupTable(self.imgArgs['lut'])
            self.img.setLevels(self.imgArgs['levels'])

    def getColormap(self):
        """Returns the currently stored colormap settings"""
        return self.imgArgs

class FFTWidget(BasePlot):
    """Widget for ploting an FFT. Does not perform an FFT, just labels axis"""
    def __init__(self, parent=None, rotation=90):
        super(FFTWidget, self).__init__(parent)
        
        self.fftPlot = self.plot(pen='k')
        self.fftPlot.rotate(rotation)
        self.getPlotItem().vb.setCustomMouse()
        self.setMouseEnabled(x=False,y=True)

        if abs(rotation) == 90:
            self.setLabel('left', 'Frequency', units='Hz')

        elif rotation == 0:
            self.setLabel('bottom', 'Frequency', units='Hz')

    def updateData(self, indexData, valueData):
        """Plot the given data

        :param indexData: index point values to match valueData array, may be plotted on x or y axis, depending on plot orientation.
        :type indexData: numpy.ndarray
        :param valueData: values to plot at indexData points, may be plotted on x or y axis, depending on plot orientation.
        :type valueData: numpy.ndarray
        """
        self.fftPlot.setData(indexData, valueData)

class SimplePlotWidget(BasePlot):
    """Generic Plot Widget"""
    def __init__(self, xdata, ydata, parent=None):
        super(SimplePlotWidget, self).__init__(parent)
        ydata = np.squeeze(ydata)
        if len(ydata.shape) > 1:
            for row in ydata:
                self.appendData(xdata, row)
        else:
            self.pdi = self.plot(xdata, ydata, pen='b')
        self.resize(800,500)

    def appendData(self, xdata, ydata):
        """Adds the data to the plot

        :param xdata: index values for data, plotted on x-axis
        :type xdata: numpy.ndarray
        :param ydata: value data to plot, dimension must match xdata
        :type ydata: numpy.ndarray
        """
        self.plot(xdata, ydata, pen='b')

    def setLabels(self, xlabel=None, ylabel=None, title=None, xunits=None, yunits=None):
        """Sets the plot labels

        :param xlabel: X-axis label (do not include units)
        :type xlabel: str
        :param ylabel: Y-axis label (do not include units)
        :type ylabel: str
        :param title: Plot title
        :type title: str
        :param xunit: SI units for the x-axis. An appropriate label will be appended according to scale
        :type xunit: str
        :param yunit: SI units for the y-axis. An appropriate label will be appended according to scale
        :type yunit: str
        """
        if xlabel is not None:
            self.setLabel('bottom', xlabel, units=xunits)
        if ylabel is not None:
            self.setLabel('left', ylabel, units=yunits)
        if title is not None:
            self.setTitle(title)

class ProgressWidget(BasePlot):
    """Widget for plotting sequential points, one at a time, for any number of given lines(groups)

    e.g. tuning curve spike counts

    :param groups: expected groups
    :type groups: list
    :param xlims: expected range of x-axis data (min, max), scales plot appropriately
    :type xlims: tuple
    """
    def __init__(self, groups, xlims=None, parent=None):
        super(ProgressWidget, self).__init__(parent)
        self.lines = []
        for iline in range(len(groups)):
            # give each line a different color
            self.lines.append(self.plot(pen=pg.intColor(iline, hues=len(groups))))

        if xlims is not None:
            self.setXlim((xlims[0], xlims[1]))
        self.groups = groups

    def setPoint(self, x, group, y):
        """Sets the given point, connects line to previous point in group

        :param x: x value of point
        :type x: float
        :param group: group which plot point for
        :type group: float
        :param y: y value of point
        :type y: float
        """
        if x == -1:
            # silence window
            self.plot([0],[y], symbol='o')
        else:
            yindex = self.groups.index(group)
            xdata, ydata = self.lines[yindex].getData()
            if ydata is None:
                xdata = [x]
                ydata = [y]
            else:
                xdata = np.append(xdata, x)
                ydata = np.append(ydata, y)
            self.lines[yindex].setData(xdata, ydata)

    def setLabels(self, name):
        """Sets plot labels, according to predefined options

        :param name: The type of plot to create labels for. Options: calibration, tuning, anything else labels for spike counts
        :type name: str
        """
        if name == "calibration":
            self.setWindowTitle("Calibration Curve")
            self.setTitle("Calibration Curve")
            self.setLabel('bottom', "Frequency", units='Hz')
            self.setLabel('left', 'Recorded Intensity (dB SPL)')
        elif name == "tuning":
            self.setWindowTitle("Tuning Curve")
            self.setTitle("Tuning Curve")
            self.setLabel('bottom', "Frequency", units="Hz")
            self.setLabel('left', "Spike Count (mean)")
        else:
            self.setWindowTitle("Spike Counts")
            self.setTitle("Spike Counts")
            self.setLabel('bottom', "Test Number", units='')
            self.setLabel('left', "Spike Count (mean)", units='')

class PSTHWidget(BasePlot):
    """Post Stimulus Time Histogram plot widget, for plotting spike counts"""
    _bins = np.arange(5)
    _counts = np.zeros((5,))
    def __init__(self, parent=None):
        super(PSTHWidget, self).__init__(parent)
        self.histo = pg.BarGraphItem(x=self._bins, height=self._counts, width=0.5)
        self.addItem(self.histo)
        self.setLabel('bottom', 'Time Bins', units='s')
        self.setLabel('left', 'Spike Counts')
        self.setXlim((0, 0.25))
        self.setYlim((0, 10))

        self.getPlotItem().vb.setZeroWheel()

    def setBins(self, bins):
        """Sets the bin centers (x values)

        :param bins: time bin centers
        :type bins: numpy.ndarray
        """
        self._bins = bins
        self._counts = np.zeros_like(self._bins)
        bar_width = bins[0]*1.5
        self.histo.setOpts(x=bins, height=self._counts, width=bar_width)
        self.setXlim((0, bins[-1]))

    def clearData(self):
        """Clears all histograms (keeps bins)"""
        self._counts = np.zeros_like(self._bins)
        self.histo.setOpts(height=self._counts)

    def appendData(self, bins, repnum=None):
        """Increases the values at bins (indexes)

        :param bins: bin center values to increment counts for, to increment a time bin more than once include multiple items in list with that bin center value
        :type bins: numpy.ndarray
        """
        # self._counts[bins] +=1 # ignores dulplicates
        for b in bins:
            self._counts[b] += 1
        self.histo.setOpts(height=self._counts)

    def getData(self):
        """Gets the heights of the histogram bars

        :returns: list<int> -- the count values for each bin
        """
        return self.histo.opts['height']

class ChartWidget(QtGui.QWidget):
    """Scrolling plot widget for continuous acquistiion display"""
    def __init__(self, parent=None):
        super(ChartWidget, self).__init__(parent)
        self.tracePlot = ScrollingWidget()
        self.stimPlot = ScrollingWidget(pencolor='b')

        self.tracePlot.setTitle('Brain Recording')
        self.stimPlot.setTitle('Stimulus Recording')
        self.tracePlot.setLabel('left', 'Potential', units='V')
        self.stimPlot.setLabel('left', ' ') # makes yaxis line up
        self.tracePlot.setLabel('bottom', 'Time', units='s')
        self.stimPlot.hideAxis('bottom')
        self.stimPlot.setXLink('Brain Recording')

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        splitter.setContentsMargins(0,0,0,0)
        splitter.addWidget(self.stimPlot)
        splitter.addWidget(self.tracePlot)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def setSr(self, sr):
        """Sets the samplerate of the input operation being plotted"""
        self.tracePlot.setSr(sr)
        self.stimPlot.setSr(sr)

    def setWindowSize(self, winsz):
        """Sets the size of scroll window"""
        self.tracePlot.setWindowSize(winsz)
        self.stimPlot.setWindowSize(winsz)

    def clearData(self):
        """Clears all data from plot"""
        self.tracePlot.clearData()
        self.stimPlot.clearData()

    def appendData(self, stim, data):
        self.tracePlot.appendData(data)
        self.stimPlot.appendData(stim)

class ScrollingWidget(BasePlot):
    def __init__(self, pencolor='k', parent=None):
        super(ScrollingWidget, self).__init__(parent)
        self.scrollPlot = self.plot(pen=pencolor)

        self.disableAutoRange()

    def setSr(self, sr):
        self._deltax = (1/float(sr))

    def setWindowSize(self, winsz):
        self._windowsize = winsz
        # set range here then?
        x0 = self.getPlotItem().viewRange()[0][0]
        self.setXlim((x0, x0+winsz))

    def clearData(self):
        self.scrollPlot.setData(None)
        self.setXlim((0, self._windowsize))

    def appendData(self, data):
        npoints_to_add = len(data)
        xdata, ydata = self.scrollPlot.getData()
        if xdata is None:
            last_time = 0
            xdata = []
            ydata = []
        else:
            last_time = xdata[-1]

        # print 'last_time', last_time, 'deltax', self.deltax, 'npoints_to_add', npoints_to_add
        # x_to_append = np.arange(last_time+self._deltax, 
        #                         last_time+self._deltax+(self._deltax*npoints_to_add),
        #                         self._deltax)
        x_to_append = np.linspace(last_time+self._deltax, 
                                  last_time+self._deltax+(self._deltax*npoints_to_add), 
                                  npoints_to_add)
        # print 'lens', len(x_to_append), len(data), len(stim), last_time, npoints_to_add
        # assert len(x_to_append) == len(data)
        # assert len(x_to_append) == len(stim)
        # print 'deltax', x_to_append[1] - x_to_append[0], self._deltax
        # assert (x_to_append[1] - x_to_append[0]) == self._deltax

        xdata = np.append(xdata, x_to_append)
        ydata = np.append(ydata, data) 

        # remove data that has gone off screen
        xlim = self.getPlotItem().viewRange()[0]
        removex, = np.where(xdata < xlim[0])

        xdata = np.delete(xdata, removex)
        ydata = np.delete(ydata, removex)

        # assuming that samplerates must be the same
        self.scrollPlot.setData(xdata, ydata)

        # now scroll axis limits
        if xlim[1] < xdata[-1]:
            xlim[1] += self._deltax*npoints_to_add
            xlim[0] += self._deltax*npoints_to_add
            self.setXlim(xlim)

class StackedPlot(QtGui.QWidget):
    """Stack a set of plots that may be flipped through using SimplePlotWidget"""
    def __init__(self, parent=None):
        super(StackedPlot, self).__init__(parent)

        self.stacker = QtGui.QStackedWidget()

        prevBtn = QtGui.QPushButton('<')
        nextBtn = QtGui.QPushButton('>')
        firstBtn = QtGui.QPushButton('|<')
        lastBtn = QtGui.QPushButton('>|')
        prevBtn.clicked.connect(self.prevPlot)
        nextBtn.clicked.connect(self.nextPlot)
        firstBtn.clicked.connect(self.firstPlot)
        lastBtn.clicked.connect(self.lastPlot)
        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addWidget(firstBtn)
        btnLayout.addWidget(prevBtn)
        btnLayout.addWidget(nextBtn)
        btnLayout.addWidget(lastBtn)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.stacker)
        layout.addLayout(btnLayout)

        # self.plots = []

    def addPlot(self, xdata, ydata, xlabel=None, ylabel=None, title=None, xunits=None, yunits=None):
        """Adds a new plot for the given set of data and/or labels, Generates a SimplePlotWidget

        :param xdata: index values for data, plotted on x-axis
        :type xdata: numpy.ndarray
        :param ydata: value data to plot, dimension must match xdata
        :type ydata: numpy.ndarray
        """
        p = SimplePlotWidget(xdata, ydata)
        p.setLabels(xlabel, ylabel, title, xunits, yunits)
        # self.plots.append(p)
        self.stacker.addWidget(p)

    def addSpectrogram(self, ydata, fs, title=None):
        """Adds a new spectorgram plot for the given image. Generates a SpecWidget

        :param ydata: 2-D array of the image to display
        :type ydata: numpy.ndarray
        :param fs: the samplerate of the signal in the image, used to set time/ frequency scale
        :type fs: int
        :param title: Plot title
        :type title: str
        """
        p = SpecWidget()
        p.updateData(ydata, fs)
        if title is not None:
            p.setTitle(title)
        self.stacker.addWidget(p)

    def nextPlot(self):
        """Moves the displayed plot to the next one"""
        if self.stacker.currentIndex() < self.stacker.count():
            self.stacker.setCurrentIndex(self.stacker.currentIndex()+1)

    def prevPlot(self):
        """Moves the displayed plot to the previous one"""
        if self.stacker.currentIndex() > 0:
            self.stacker.setCurrentIndex(self.stacker.currentIndex()-1)

    def firstPlot(self):
        """Jumps display plot to the first one"""
        self.stacker.setCurrentIndex(0)

    def lastPlot(self):
        """Jumps display plot to the last one"""
        self.stacker.setCurrentIndex(self.stacker.count()-1)