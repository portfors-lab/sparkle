from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

from spikeylab.dialogs.raster_bounds_dlg import RasterBoundsDialog
import spikeylab.tools.audiotools as audiotools

STIM_HEIGHT = 0.10

## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(useWeave=False)

class TraceWidget(pg.PlotWidget):
    tscale = 1. # s
    nreps = 20
    raster_ymin = 0.5
    raster_ymax = 1
    raster_yslots = np.linspace(raster_ymin, raster_ymax, nreps)
    threshold_updated = QtCore.pyqtSignal(float)
    def __init__(self, parent=None):
        super(TraceWidget, self).__init__(parent)

        # self.pw = pg.PlotWidget(name='trace')
        self.trace_plot = self.plot(pen='k')
        self.raster_plot = self.plot(pen=None, symbol='s', symbolPen=None, symbolSize=4, symbolBrush='k')
        self.stim_plot = self.plot(pen='b')

        self.sigRangeChanged.connect(self.range_change)

        self.disableAutoRange()
        self.setMouseEnabled(x=False,y=True)

        # print 'scene', self.scene().contextMenu[0].text()
        # # self.scene().contextMenu = []
        # print 'items', 
        # for act in self.getPlotItem().ctrlMenu.actions():
        #     print act.text()
        # print '-'*20
        # for act in self.getPlotItem().vb.menu.actions():
        #     print act.text()
        # print '-'*20
        # because of pyqtgraph internals, we can't just remove action from menu
        self.fake_action = QtGui.QAction("", None)
        self.getPlotItem().vb.menu.leftMenu = self.fake_action
        self.fake_action.setCheckable(True)
        self.getPlotItem().vb.menu.mouseModes = [self.fake_action]

        raster_bounds_action = QtGui.QAction("edit raster bounds", None)
        self.scene().contextMenu.append(raster_bounds_action) #should use function for this?
        raster_bounds_action.triggered.connect(self.ask_raster_bounds)

        xaxis = self.getPlotItem().getAxis('bottom')
        self.timeTickStrings = xaxis.tickStrings
        xaxis.tickStrings = self.time_tick_strings

        self.thresh_line = pg.InfiniteLine(pos=0.5, angle=0, pen='r', movable=True)
        self.addItem(self.thresh_line)
        self.thresh_line.sigPositionChangeFinished.connect(self.update_thresh)

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
            # adjust repetition number to response scale
            ypoints = np.ones_like(ypoints)*self.raster_yslots[ypoints[0]]
            x = np.append(x, bins)
            y = np.append(y, ypoints)
            self.raster_plot.setData(x, y)

    def clear_data(self, axeskey):
        # if axeskey == 'response':
        self.raster_plot.clear()

    def set_xlim(self, lim):
        lim = (lim[0], lim[1])
        self.setXRange(*lim, padding=0)

    def set_ylim(self, lim):
        self.setYRange(*lim)

    def get_threshold(self):
        x, y = self.tresh_line.getData()
        return y[0]

    def set_threshold(self, threshold):
        self.thresh_line.setValue(threshold) 

    def set_nreps(self, nreps):
        self.nreps = nreps

    def set_raster_bounds(self,lims):
        self.raster_ymin = lims[0]
        self.raster_ymax = lims[1]
        self.raster_yslots = np.linspace(self.raster_ymin, self.raster_ymax, self.nreps)

    def ask_raster_bounds(self):
        dlg = RasterBoundsDialog(bounds= (self.raster_ymin, self.raster_ymax))
        if dlg.exec_():
            bounds = dlg.get_values()
            self.set_raster_bounds(bounds)
            print bounds

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
                stim_y = stim_y/np.amax(stim_y)
                # scale for new size
                stim_y = stim_y*stim_height
                # raise to right place in plot
                stim_y = stim_y + (ranges[1][1] - (stim_height*1.1 + (stim_height*0.2)))
                self.stim_plot.setData(stim_x, stim_y)

    def set_tscale(self, scale):
        self.tscale = scale
        xlim = self.viewRange()[0]
        if self.tscale == 0.001:
            self.time_label = 'Time (ms)'
        elif self.tscale == 1:
            self.time_label = 'Time (s)'
        else:
            raise Exception(u"Invalid time scale")

    def time_tick_strings(self, vales, scale, spacing):
        ticks = self.timeTickStrings(vales, scale, spacing)
        ticks = [str(float(x)/self.tscale) for x in ticks]
        return ticks

    def update_thresh(self):
        self.threshold_updated.emit(self.thresh_line.value())

class SpecWidget(pg.PlotWidget):
    specgram_args = {u'nfft':512, u'window':u'hanning', u'overlap':90}
    img_args = {'cmap':'jet'}
    reset_image_scale = True
    img_scale = (1.,1.)
    tscale = 1. # s
    fscale = 1000
    def __init__(self, parent=None):
        super(SpecWidget, self).__init__(parent)

        self.img = pg.ImageItem()
        self.addItem(self.img)

        self.setMouseEnabled(x=False,y=True)
        self.sigScaleChanged.connect(self.scale_change)

        yaxis = self.getPlotItem().getAxis('left')
        self.tickStrings = yaxis.tickStrings
        yaxis.tickStrings = self.tick_strings

        xaxis = self.getPlotItem().getAxis('bottom')
        self.timeTickStrings = xaxis.tickStrings
        xaxis.tickStrings = self.time_tick_strings

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

    def reset_scale(self):
        self.img.scale(1./self.img_scale[0], 1./self.img_scale[1])
        self.img_scale = (1.,1.)

    def update_data(self, signal, fs):
        spec, f, bins, dur = audiotools.spectrogram((fs, signal), **self.specgram_args)
        self.update_image(spec, bins, f)

    def set_spec_args(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'colormap':
                self.img_args['cmap'] = value
            else:
                self.specgram_args[key] = value

    def set_xlim(self, lim):
        self.setXRange(*lim, padding=0)

    def scale_change(self, obj):
        print 'scale change', obj

    def clear(self):
        pass

    def set_fscale(self, scale):
        self.fscale = scale
        if self.fscale == 1000:
            self.freq_title = u'Frequency (kHz)'
        elif self.fscale == 1:
            self.freq_title = u'Frequency (Hz)'
        else:
            raise Exception(u"Invalid frequency scale")

    def set_tscale(self, scale):
        self.tscale = scale
        xlim = self.viewRange()[0]
        if self.tscale == 0.001:
            self.time_label = 'Time (ms)'
        elif self.tscale == 1:
            self.time_label = 'Time (s)'
        else:
            raise Exception(u"Invalid time scale")

    def tick_strings(self, vales, scale, spacing):
        ticks = self.tickStrings(vales, scale, spacing)
        ticks = [str(float(x)/self.fscale) for x in ticks]
        return ticks

    def time_tick_strings(self, vales, scale, spacing):
        ticks = self.timeTickStrings(vales, scale, spacing)
        ticks = [str(float(x)/self.tscale) for x in ticks]
        return ticks

class FFTWidget(pg.PlotWidget):
    fscale = 1000
    freq_label = 'Frequency (kHz)'
    def __init__(self, parent=None, rotation=90):
        super(FFTWidget, self).__init__(parent)
        
        self.fft_plot = self.plot(pen='k')
        self.fft_plot.rotate(rotation)

        xaxis = self.getPlotItem().getAxis('left')
        self.tickStrings = xaxis.tickStrings
        xaxis.tickStrings = self.tick_strings

    def update_data(self, index_data, value_data):
        self.fft_plot.setData(index_data, value_data)

    def set_fscale(self, scale):
        self.fscale = scale
        if self.fscale == 1000:
            self.freq_title = u'Frequency (kHz)'
        elif self.fscale == 1:
            self.freq_title = u'Frequency (Hz)'
        else:
            raise Exception(u"Invalid frequency scale")

    def tick_strings(self, vales, scale, spacing):
        ticks = self.tickStrings(vales, scale, spacing)
        ticks = [str(float(x)/self.fscale) for x in ticks]
        return ticks