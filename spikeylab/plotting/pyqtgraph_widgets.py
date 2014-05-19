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

    def set_tscale(self, scale):
        pass

    def set_fscale(self, scale):
        pass

    def set_xlim(self, lim):
        self.setXRange(*lim, padding=0)

    def set_ylim(self, lim):
        self.setYRange(*lim)

    def set_title(self, title):
        self.getPlotItem().setTitle(title)


class TraceWidget(BasePlot):
    nreps = 20
    raster_ymin = 0.5
    raster_ymax = 1
    raster_yslots = np.linspace(raster_ymin, raster_ymax, nreps)
    threshold_updated = QtCore.pyqtSignal(float)
    def __init__(self, parent=None):
        super(TraceWidget, self).__init__(parent)

        self.trace_plot = self.plot(pen='k')
        self.raster_plot = self.plot(pen=None, symbol='s', symbolPen=None, symbolSize=4, symbolBrush='k')
        self.stim_plot = self.plot(pen='b')
        self.stim_plot.curve.setToolTip("Stimulus Signal")
        self.trace_plot.curve.setToolTip("Spike Trace")

        self.sigRangeChanged.connect(self.range_change)

        self.disableAutoRange()

        raster_bounds_action = QtGui.QAction("Edit raster bounds", None)
        self.scene().contextMenu.append(raster_bounds_action) #should use function for this?
        raster_bounds_action.triggered.connect(self.ask_raster_bounds)

        self.thresh_line = pg.InfiniteLine(pos=0.5, angle=0, pen='r', movable=True)
        self.addItem(self.thresh_line)
        self.thresh_line.sigPositionChangeFinished.connect(self.update_thresh)
        self.setLabel('left', 'Potential', units='V')
        self.setLabel('bottom', 'Time', units='s')

    def update_data(self, axeskey, x, y):
        if axeskey == 'stim':
            self.stim_plot.setData(x,y)
            # call manually to ajust placement of signal
            ranges = self.viewRange()
            self.range_change(self, ranges)
        if axeskey == 'response':
            self.trace_plot.setData(x,y)

    def append_data(self, axeskey, bins, ypoints):
        if axeskey == 'raster':
            x, y = self.raster_plot.getData()
            # don't plot overlapping points
            bins = np.unique(bins)
            # adjust repetition number to response scale
            ypoints = np.ones_like(bins)*self.raster_yslots[ypoints[0]]
            x = np.append(x, bins)
            y = np.append(y, ypoints)
            self.raster_plot.setData(x, y)

    def clear_data(self, axeskey):
        # if axeskey == 'response':
        self.raster_plot.clear()

    def get_threshold(self):
        x, y = self.tresh_line.getData()
        return y[0]

    def set_threshold(self, threshold):
        self.thresh_line.setValue(threshold) 

    def set_nreps(self, nreps):
        self.nreps = nreps
        self.raster_yslots = np.linspace(self.raster_ymin, self.raster_ymax, self.nreps)

    def set_raster_bounds(self,lims):
        self.raster_ymin = lims[0]
        self.raster_ymax = lims[1]
        self.raster_yslots = np.linspace(self.raster_ymin, self.raster_ymax, self.nreps)

    def ask_raster_bounds(self):
        dlg = RasterBoundsDialog(bounds= (self.raster_ymin, self.raster_ymax))
        if dlg.exec_():
            bounds = dlg.get_values()
            self.set_raster_bounds(bounds)

    def get_raster_bounds(self):
        return (self.raster_ymin, self.raster_ymax)

    def set_title(self, title):
        pass

    def range_change(self, pw, ranges):
        if hasattr(ranges, '__iter__'):
            # adjust the stim signal so that it falls in the correct range
            stim_x, stim_y = self.stim_plot.getData()
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
                self.stim_plot.setData(stim_x, stim_y)

    def update_thresh(self):
        self.threshold_updated.emit(self.thresh_line.value())

class SpecWidget(BasePlot):
    specgram_args = {u'nfft':512, u'window':u'hanning', u'overlap':90}
    img_args = {'lut':None, 'state':None, 'levels':None}
    reset_image_scale = True
    img_scale = (1.,1.)
    colormap_changed = QtCore.pyqtSignal(object)
    def __init__(self, parent=None):
        super(SpecWidget, self).__init__(parent)

        self.img = pg.ImageItem()
        self.addItem(self.img)

        cmap_action = QtGui.QAction("Edit colormap", None)
        self.scene().contextMenu.append(cmap_action) #should use function for this?
        cmap_action.triggered.connect(self.edit_colormap)

        self.setLabel('bottom', 'Time', units='s')
        self.setLabel('left', 'Frequency', units='Hz')

    def from_file(self, fname):
        spec, f, bins, dur = audiotools.spectrogram(fname, **self.specgram_args)
        self.update_image(spec, bins, f)
        return dur

    def update_image(self, imgdata, xaxis=None, yaxis=None):
        imgdata = imgdata.T
        self.img.setImage(imgdata)
        if xaxis is not None and yaxis is not None:
            xscale = 1.0/(imgdata.shape[0]/xaxis[-1])
            yscale = 1.0/(imgdata.shape[1]/yaxis[-1])
            self.reset_scale()        
            self.img.scale(xscale, yscale)
            self.img_scale = (xscale, yscale)
        self.image_array = np.fliplr(imgdata)
        self.update_colormap()

    def reset_scale(self):
        self.img.scale(1./self.img_scale[0], 1./self.img_scale[1])
        self.img_scale = (1.,1.)

    def update_data(self, signal, fs):
        spec, f, bins, dur = audiotools.spectrogram((fs, signal), **self.specgram_args)
        self.update_image(spec, bins, f)

    def set_spec_args(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'colormap':
                self.img_args['lut'] = value['lut']
                self.img_args['levels'] = value['levels']
                self.img_args['state'] = value['state']
                self.update_colormap()
            else:
                self.specgram_args[key] = value

    def clear_img(self):
        self.img.image = None
        # self.img.setImage(np.array([[0]]))

    def has_img(self):
        return self.img.image is not None

    def edit_colormap(self):
        self.editor = pg.ImageView()
        # remove the ROI and Norm buttons
        self.editor.ui.roiBtn.setVisible(False)
        self.editor.ui.normBtn.setVisible(False)
        self.editor.setImage(self.image_array)
        if self.img_args['state'] is not None:
            self.editor.getHistogramWidget().item.gradient.restoreState(self.img_args['state'])
            self.editor.getHistogramWidget().item.setLevels(*self.img_args['levels'])
        
        self.editor.closeEvent = self.editor_close
        self.editor.show()

    def editor_close(self, event):
        lut = self.editor.getHistogramWidget().item.getLookupTable(n=512, alpha=True)
        state = self.editor.getHistogramWidget().item.gradient.saveState()
        levels = self.editor.getHistogramWidget().item.getLevels()
        self.img.setLookupTable(lut)
        self.img.setLevels(levels)
        self.img_args['lut'] = lut
        self.img_args['state'] = state
        self.img_args['levels'] = levels
        self.colormap_changed.emit(self.img_args)

    def update_colormap(self):
        if self.img_args['lut'] is not None:
            self.img.setLookupTable(self.img_args['lut'])
            self.img.setLevels(self.img_args['levels'])

    def get_colormap(self):
        return self.img_args

class FFTWidget(BasePlot):
    def __init__(self, parent=None, rotation=90):
        super(FFTWidget, self).__init__(parent)
        
        self.fft_plot = self.plot(pen='k')
        self.fft_plot.rotate(rotation)
        self.getPlotItem().vb.set_custom_mouse()

        if abs(rotation) == 90:
            self.setLabel('left', 'Frequency', units='Hz')
            self.setMouseEnabled(x=False,y=True)

        elif rotation == 0:
            self.setLabel('bottom', 'Frequency', units='Hz')
            self.setMouseEnabled(x=False,y=True)

    def update_data(self, index_data, value_data):
        self.fft_plot.setData(index_data, value_data)

class SimplePlotWidget(BasePlot):
    def __init__(self, xpoints, ypoints, parent=None):
        super(SimplePlotWidget, self).__init__(parent)
        ypoints = np.squeeze(ypoints)
        if len(ypoints.shape) > 1:
            for row in ypoints:
                self.append_data(xpoints, row)
        else:
            self.pdi = self.plot(xpoints, ypoints, pen='k')
        self.resize(800,500)

    def append_data(self, xpoints, ypoints):
        self.plot(xpoints, ypoints, pen='k')

    def set_labels(self, xlabel=None, ylabel=None, title=None, xunits=None, yunits=None):
        if xlabel is not None:
            self.setLabel('bottom', xlabel, units=xunits)
        if ylabel is not None:
            self.setLabel('left', ylabel, units=yunits)
        if title is not None:
            self.set_title(title)

class ProgressWidget(BasePlot):
    def __init__(self, xpoints, ypoints, parent=None):
        super(ProgressWidget, self).__init__(parent)
        self.lines = []
        for iline in range(len(ypoints)):
            # give each line a different color
            self.lines.append(self.plot(pen=pg.intColor(iline, hues=len(ypoints))))

        self.set_xlim((xpoints[0], xpoints[-1]))
        self.xpoints = xpoints
        self.ypoints = ypoints

    def set_point(self, x, y, value):
        yindex = self.ypoints.index(y)
        xdata, ydata = self.lines[yindex].getData()
        if ydata is None:
            xdata = [x]
            ydata = [value]
        else:
            xdata = np.append(xdata, x)
            ydata = np.append(ydata, value)
        self.lines[yindex].setData(xdata, ydata)

    def set_labels(self, name):
        if name == "calibration":
            self.setWindowTitle("Calibration Curve")
            self.set_title("Calibration Curve")
            self.setLabel('bottom', "Frequency", units='Hz')
            self.setLabel('left', 'Recorded Intensity (dB SPL)')
        elif name == "tuning":
            self.setWindowTitle("Tuning Curve")
            self.set_title("Tuning Curve")
            self.setLabel('bottom', "Frequency", units="Hz")
            self.setLabel('left', "Spike Count (mean)")
        else:
            self.setWindowTitle("Spike Counts")
            self.set_title("Spike Counts")
            self.setLabel('bottom', "Test Number")
            self.setLabel('left', "Spike Count (mean)")

class PSTHWidget(BasePlot):
    _bins = np.arange(5)
    _counts = np.zeros((5,))
    def __init__(self, parent=None):
        super(PSTHWidget, self).__init__(parent)
        self.histo = pg.BarGraphItem(x=self._bins, height=self._counts, width=0.5)
        self.addItem(self.histo)
        self.setLabel('bottom', 'Time Bins', units='s')
        self.setLabel('left', 'Spike Counts')
        self.set_xlim((0, 0.25))
        self.set_ylim((0, 10))

        self.getPlotItem().vb.set_zero_wheel()

    def set_bins(self, bins):
        """Set the bin centers (x values)"""
        self._bins = bins
        self._counts = np.zeros_like(self._bins)
        bar_width = bins[0]*1.5
        self.histo.setOpts(x=bins, height=self._counts, width=bar_width)
        self.set_xlim((0, bins[-1]))

    def clear_data(self):
        """Clear all histograms (keep bins)"""
        self._counts = np.zeros_like(self._bins)
        self.histo.setOpts(height=self._counts)

    def append_data(self, bins, repnum=None):
        """Increase the values at bins (indexes)"""
        # self._counts[bins] +=1 # ignores dulplicates
        for b in bins:
            self._counts[b] += 1
        self.histo.setOpts(height=self._counts)

class ChartWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ChartWidget, self).__init__(parent)
        self.trace_plot = ScrollingWidget()
        self.stim_plot = ScrollingWidget(pencolor='b')

        self.trace_plot.set_title('Brain Recording')
        self.stim_plot.set_title('Stimulus Recording')
        self.trace_plot.setLabel('left', 'Potential', units='V')
        self.stim_plot.setLabel('left', ' ') # makes yaxis line up
        self.trace_plot.setLabel('bottom', 'Time', units='s')
        self.stim_plot.hideAxis('bottom')
        self.stim_plot.setXLink('Brain Recording')

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        splitter.setContentsMargins(0,0,0,0)
        splitter.addWidget(self.stim_plot)
        splitter.addWidget(self.trace_plot)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def set_sr(self, sr):
        self.trace_plot.set_sr(sr)
        self.stim_plot.set_sr(sr)

    def set_windowsize(self, winsz):
        self.trace_plot.set_windowsize(winsz)
        self.stim_plot.set_windowsize(winsz)

    def clear_data(self):
        self.trace_plot.clear_data()
        self.stim_plot.clear_data()

    def append_data(self, stim, data):
        self.trace_plot.append_data(data)
        self.stim_plot.append_data(stim)

class ScrollingWidget(BasePlot):
    def __init__(self, pencolor='k', parent=None):
        super(ScrollingWidget, self).__init__(parent)
        self.scroll_plot = self.plot(pen=pencolor)

        self.disableAutoRange()

    def set_sr(self, sr):
        self._deltax = (1/float(sr))

    def set_windowsize(self, winsz):
        self._windowsize = winsz
        # set range here then?
        x0 = self.getPlotItem().viewRange()[0][0]
        self.set_xlim((x0, x0+winsz))

    def clear_data(self):
        self.scroll_plot.setData(None)
        self.set_xlim((0, self._windowsize))

    def append_data(self, data):
        npoints_to_add = len(data)
        xdata, ydata = self.scroll_plot.getData()
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
        self.scroll_plot.setData(xdata, ydata)

        # now scroll axis limits
        if xlim[1] < xdata[-1]:
            xlim[1] += self._deltax*npoints_to_add
            xlim[0] += self._deltax*npoints_to_add
            self.set_xlim(xlim)

class StackedPlot(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StackedPlot, self).__init__(parent)

        self.stacker = QtGui.QStackedWidget()

        prev_btn = QtGui.QPushButton('<')
        next_btn = QtGui.QPushButton('>')
        first_btn = QtGui.QPushButton('|<')
        last_btn = QtGui.QPushButton('>|')
        prev_btn.clicked.connect(self.prev_plot)
        next_btn.clicked.connect(self.next_plot)
        first_btn.clicked.connect(self.first_plot)
        last_btn.clicked.connect(self.last_plot)
        btn_layout = QtGui.QHBoxLayout()
        btn_layout.addWidget(first_btn)
        btn_layout.addWidget(prev_btn)
        btn_layout.addWidget(next_btn)
        btn_layout.addWidget(last_btn)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.stacker)
        layout.addLayout(btn_layout)

        # self.plots = []

    def add_plot(self, xdata, ydata, xlabel=None, ylabel=None, title=None, xunits=None, yunits=None):
        p = SimplePlotWidget(xdata, ydata)
        p.set_labels(xlabel, ylabel, title, xunits, yunits)
        # self.plots.append(p)
        self.stacker.addWidget(p)

    def add_spectrogram(self, ydata, fs, title=None):
        p = SpecWidget()
        p.update_data(ydata, fs)
        if title is not None:
            p.set_title(title)
        self.stacker.addWidget(p)

    def next_plot(self):
        if self.stacker.currentIndex() < self.stacker.count():
            self.stacker.setCurrentIndex(self.stacker.currentIndex()+1)

    def prev_plot(self):
        if self.stacker.currentIndex() > 0:
            self.stacker.setCurrentIndex(self.stacker.currentIndex()-1)

    def first_plot(self):
        self.stacker.setCurrentIndex(0)

    def last_plot(self):
        self.stacker.setCurrentIndex(self.stacker.count()-1)