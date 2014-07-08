from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

from spikeylab.plotting.viewbox import SpikeyViewBox
from spikeylab.plotting.raster_bounds_dlg import RasterBoundsDialog
import spikeylab.tools.audiotools as audiotools

STIM_HEIGHT = 0.05

## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(useWeave=False)

class BasePlot(pg.PlotWidget):
    def __init__(self, parent=None):
        super(BasePlot, self).__init__(parent, viewBox=SpikeyViewBox())

        # print 'scene', self.scene().contextMenu[0].text()
        # # self.scene().contextMenu = []
        # print 'items', 
        for act in self.getPlotItem().ctrlMenu.actions():
            # print act.text()
            if act.text() != 'Grid':
                self.getPlotItem().ctrlMenu.removeAction(act)
        # print '-'*20
        # for act in self.getPlotItem().vb.menu.actions():
        #     if act.text() != 'View All':
        #         print 'removing', act.text()
        #         self.getPlotItem().vb.menu.removeAction(act)
        # print '-'*20
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
        if axeskey == 'stim':
            self.stimPlot.setData(x,y)
            # call manually to ajust placement of signal
            ranges = self.viewRange()
            self.rangeChange(self, ranges)
        if axeskey == 'response':
            self.tracePlot.setData(x,y)

    def appendData(self, axeskey, bins, ypoints):
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
        # if axeskey == 'response':
        self.rasterPlot.clear()

    def getThreshold(self):
        y = self.threshLine.value()
        return y

    def setThreshold(self, threshold):
        self.threshLine.setValue(threshold) 

    def setNreps(self, nreps):
        self.nreps = nreps
        self.rasterYslots = np.linspace(self.rasterYmin, self.rasterYmax, self.nreps)

    def setRasterBounds(self,lims):
        self.rasterYmin = lims[0]
        self.rasterYmax = lims[1]
        self.rasterYslots = np.linspace(self.rasterYmin, self.rasterYmax, self.nreps)

    def askRasterBounds(self):
        dlg = RasterBoundsDialog(bounds= (self.rasterYmin, self.rasterYmax))
        if dlg.exec_():
            bounds = dlg.values()
            self.setRasterBounds(bounds)

    def getRasterBounds(self):
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
        self.thresholdUpdated.emit(self.threshLine.value())

class SpecWidget(BasePlot):
    specgramArgs = {u'nfft':512, u'window':u'hanning', u'overlap':90}
    imgArgs = {'lut':None, 'state':None, 'levels':None}
    resetImageScale = True
    imgScale = (1.,1.)
    colormapChanged = QtCore.pyqtSignal(object)
    def __init__(self, parent=None):
        super(SpecWidget, self).__init__(parent)

        self.img = pg.ImageItem(autoDownsample=True)
        self.addItem(self.img)
        self.imageArray = np.array([[0]])

        cmapAction = QtGui.QAction("Edit colormap", None)
        self.scene().contextMenu.append(cmapAction) #should use function for this?
        cmapAction.triggered.connect(self.editColormap)

        self.setLabel('bottom', 'Time', units='s')
        self.setLabel('left', 'Frequency', units='Hz')

    def fromFile(self, fname):
        spec, f, bins, dur = audiotools.spectrogram(fname, **self.specgramArgs)
        self.updateImage(spec, bins, f)
        return dur

    def updateImage(self, imgdata, xaxis=None, yaxis=None):
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
        self.img.scale(1./self.imgScale[0], 1./self.imgScale[1])
        self.imgScale = (1.,1.)

    def updateData(self, signal, fs):
        spec, f, bins, dur = audiotools.spectrogram((fs, signal), **self.specgramArgs)
        self.updateImage(spec, bins, f)

    def setSpecArgs(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'colormap':
                self.imgArgs['lut'] = value['lut']
                self.imgArgs['levels'] = value['levels']
                self.imgArgs['state'] = value['state']
                self.updateColormap()
            else:
                self.specgramArgs[key] = value

    def clearImg(self):
        self.img.setImage(np.array([[0]]))
        self.img.image = None

    def hasImg(self):
        return self.img.image is not None

    def editColormap(self):
        self.editor = pg.ImageView()
        # remove the ROI and Norm buttons
        self.editor.ui.roiBtn.setVisible(False)
        self.editor.ui.normBtn.setVisible(False)
        self.editor.setImage(self.imageArray)
        if self.imgArgs['state'] is not None:
            self.editor.getHistogramWidget().item.gradient.restoreState(self.imgArgs['state'])
            self.editor.getHistogramWidget().item.setLevels(*self.imgArgs['levels'])
        
        self.editor.closeEvent = self.editor_close
        self.editor.show()

    def editor_close(self, event):
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
        if self.imgArgs['lut'] is not None:
            self.img.setLookupTable(self.imgArgs['lut'])
            self.img.setLevels(self.imgArgs['levels'])

    def getColormap(self):
        return self.imgArgs

class FFTWidget(BasePlot):
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
        self.fftPlot.setData(indexData, valueData)

class SimplePlotWidget(BasePlot):
    def __init__(self, xpoints, ypoints, parent=None):
        super(SimplePlotWidget, self).__init__(parent)
        ypoints = np.squeeze(ypoints)
        if len(ypoints.shape) > 1:
            for row in ypoints:
                self.appendData(xpoints, row)
        else:
            self.pdi = self.plot(xpoints, ypoints, pen='b')
        self.resize(800,500)

    def appendData(self, xpoints, ypoints):
        self.plot(xpoints, ypoints, pen='b')

    def setLabels(self, xlabel=None, ylabel=None, title=None, xunits=None, yunits=None):
        if xlabel is not None:
            self.setLabel('bottom', xlabel, units=xunits)
        if ylabel is not None:
            self.setLabel('left', ylabel, units=yunits)
        if title is not None:
            self.setTitle(title)

class ProgressWidget(BasePlot):
    def __init__(self, xpoints, ypoints, parent=None):
        super(ProgressWidget, self).__init__(parent)
        self.lines = []
        for iline in range(len(ypoints)):
            # give each line a different color
            self.lines.append(self.plot(pen=pg.intColor(iline, hues=len(ypoints))))

        self.setXlim((xpoints[0], xpoints[-1]))
        self.xpoints = xpoints
        self.ypoints = ypoints

    def setPoint(self, x, y, value):
        yindex = self.ypoints.index(y)
        xdata, ydata = self.lines[yindex].getData()
        if ydata is None:
            xdata = [x]
            ydata = [value]
        else:
            xdata = np.append(xdata, x)
            ydata = np.append(ydata, value)
        self.lines[yindex].setData(xdata, ydata)

    def setLabels(self, name):
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
        """Set the bin centers (x values)"""
        self._bins = bins
        self._counts = np.zeros_like(self._bins)
        bar_width = bins[0]*1.5
        self.histo.setOpts(x=bins, height=self._counts, width=bar_width)
        self.setXlim((0, bins[-1]))

    def clearData(self):
        """Clear all histograms (keep bins)"""
        self._counts = np.zeros_like(self._bins)
        self.histo.setOpts(height=self._counts)

    def appendData(self, bins, repnum=None):
        """Increase the values at bins (indexes)"""
        # self._counts[bins] +=1 # ignores dulplicates
        for b in bins:
            self._counts[b] += 1
        self.histo.setOpts(height=self._counts)

    def getData(self):
        return self.histo.opts['height']

class ChartWidget(QtGui.QWidget):
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
        self.tracePlot.setSr(sr)
        self.stimPlot.setSr(sr)

    def setWindowSize(self, winsz):
        self.tracePlot.setWindowSize(winsz)
        self.stimPlot.setWindowSize(winsz)

    def clearData(self):
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
        p = SimplePlotWidget(xdata, ydata)
        p.setLabels(xlabel, ylabel, title, xunits, yunits)
        # self.plots.append(p)
        self.stacker.addWidget(p)

    def addSpectrogram(self, ydata, fs, title=None):
        p = SpecWidget()
        p.updateData(ydata, fs)
        if title is not None:
            p.setTitle(title)
        self.stacker.addWidget(p)

    def nextPlot(self):
        if self.stacker.currentIndex() < self.stacker.count():
            self.stacker.setCurrentIndex(self.stacker.currentIndex()+1)

    def prevPlot(self):
        if self.stacker.currentIndex() > 0:
            self.stacker.setCurrentIndex(self.stacker.currentIndex()-1)

    def firstPlot(self):
        self.stacker.setCurrentIndex(0)

    def lastPlot(self):
        self.stacker.setCurrentIndex(self.stacker.count()-1)