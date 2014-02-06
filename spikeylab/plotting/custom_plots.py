import sys

from traits.api import HasTraits, Instance, List, Int, Tuple, Float, Trait, Class, Property
from traitsui.api import View, Item
from chaco.api import Plot, ArrayPlotData, OverlayPlotContainer, DataRange1D, PlotLabel
from enable.component_editor import ComponentEditor
from enthought.enable.api import Window, Component
from chaco.tools.api import PanTool, ZoomTool, BroadcasterTool, DragZoom
from enthought.chaco.tools.rect_zoom import RectZoomTool
from enthought.chaco import default_colormaps

import numpy as np
from scipy.special import jn

from spikeylab.plotting.plottools import SpikeTraceBroadcasterTool, LineDraggingTool, AxisZoomTool
import spikeylab.tools.audiotools as audiotools

from PyQt4 import QtCore, QtGui

from spikeylab.tools.qthreading import ProtocolSignals
from spikeylab.dialogs.raster_bounds_dlg import RasterBoundsDialog

LEFT_MARGIN = 50
RIGHT_MARGIN = 10

DEFAULT_NREPS = 20
RASTER_YMAX = 1
RASTER_YMIN = 0.5

def append(arr, data):
    if isinstance(arr, list):
        arr.extend(list(data))
    elif isinstance(arr, np.ndarray):
        arr = np.append(arr, data)
    return arr

class BaseWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        trait_object = self._create_plotter()
        self.window = Window(self, -1, component=trait_object.plot)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.window.control)
        self.setLayout(layout)
        self.traits = trait_object
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuRequested)

    def _create_plotter(self):
        raise NotImplementedError

    def contextMenuRequested(self, point):
        raise NotImplementedError

    def update_data(self, *args, **kwargs):
        self.traits.update_data(*args, **kwargs)

    def append_data(self, *args, **kwargs):
        self.traits.append_data(*args, **kwargs)

    def set_xlim(self, *args, **kwargs):
        self.traits.set_xlim(*args, **kwargs)

    def clear_data(self, *args, **kwargs):
        self.traits.clear_data(*args, **kwargs)

    def set_title(self, title):
        # Add the title at the top
        self.traits.set_title(title)

    def sizeHint(self):
        return QtCore.QSize(500, 300)

class SimpleTraceWidget(BaseWidget):
    def _create_plotter(self):
        return LinePlotter()

    def contextMenuRequested(self, point):
        menu = QtGui.QMenu()
        axis_action = menu.addAction("reset axis limits")
        axis_action.triggered.connect(self.traits.reset_lims)
        menu.exec_(self.mapToGlobal(point))

class FFTWidget(BaseWidget):
    def _create_plotter(self):
        self.setToolTip('FFT of stimulus signal')
        return FFTPlotter()

    def contextMenuRequested(self, point):
        menu = QtGui.QMenu()
        axis_action = menu.addAction("reset axis limits")
        axis_action.triggered.connect(self.traits.reset_lims)
        menu.exec_(self.mapToGlobal(point))

class TraceWidget(BaseWidget):
    autoscale_action = QtGui.QAction('auto-scale axes',None)
    autoscale_action.setCheckable(False)
    def _create_plotter(self):
        self.autoscale_action.triggered.connect(self.toggle_autoscale)
        return SpikePlotter()
    
    def resizeEvent(self, event):
        margin = self.traits.trace_plot.padding_left
        vpos = event.size().height() - self.traits.trace_plot.padding_bottom \
                                     - self.traits.trace_plot.padding_top \
                                     - self.traits.stim_plot_height
        self.traits.stim_plot.set(position=[margin,vpos]) 

    def contextMenuRequested(self, point):
        menu = QtGui.QMenu()
        axis_action = menu.addAction("reset axis limits")
        axis_action.triggered.connect(self.traits.reset_lims)
        raster_bounds_action = menu.addAction("edit raster bounds")
        raster_bounds_action.triggered.connect(self.ask_raster_bounds)
        menu.addAction(self.autoscale_action)
        
        menu.exec_(self.mapToGlobal(point))

    def get_threshold(self):
        return self.traits.trace_data.get_data('threshold')

    def set_threshold(self, threshold):
        self.traits.trace_data.set_data('threshold', [threshold, threshold])
        print 'thresh anchor', self.traits.trace_data.get_data('thresh_anchor')

    def set_nreps(self, nreps):
        self.traits.nreps = nreps

    def set_raster_bounds(self,lims):
        self.traits.raster_ymin = lims[0]
        self.traits.raster_ymax = lims[1]

    def ask_raster_bounds(self):
        dlg = RasterBoundsDialog(bounds= (self.traits.raster_ymin, self.traits.raster_ymax))
        if dlg.exec_():
            bounds = dlg.get_values()
            self.set_raster_bounds(bounds)

    def get_raster_bounds(self):
        return (self.traits.raster_ymin, self.traits.raster_ymax)

    def toggle_autoscale(self, checked):
            self.traits.trace_plot.range2d.x_range.reset()
            self.traits.trace_plot.range2d.y_range.reset()

class SpecWidget(BaseWidget):
    specgram_args = {u'nfft':512, u'window':u'hanning', u'overlap':90}
    def _create_plotter(self):
        self.setToolTip('Spectrogram of stimulus signal')
        return ImagePlotter()

    def from_file(self, filename):
        spec, f, bins, dur = audiotools.spectrogram(filename, **self.specgram_args)
        self.traits.update_data(spec, xaxis=bins, yaxis=f)
        return dur

    def update_data(self, signal, fs):
        spec, f, bins, dur = audiotools.spectrogram((fs, signal), **self.specgram_args)
        self.traits.update_data(spec, xaxis=bins, yaxis=f)

    def clear(self):
        self.traits.update_data([[0]])

    def set_spec_args(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'colormap':
                self.traits.set_colormap(value)
            else:
                self.specgram_args[key] = value

class ChartWidget(BaseWidget):
    def _create_plotter(self):
        return ScrollingPlotter()

    def set_sr(self, sr):
        self.traits.set_time_delta(1/float(sr))

    def set_windowsize(self, winsz):
        self.traits.set_windowsize(winsz)

    def resizeEvent(self, event):
        margin = self.traits.response_plot.padding_left
        vpos = event.size().height() - self.traits.response_plot.padding_bottom \
                                     - self.traits.response_plot.padding_top \
                                     - self.traits.stim_plot_height
        self.traits.stim_plot.set(position=[margin,vpos]) 

class PSTHWidget(BaseWidget):
    def _create_plotter(self):
        return PSTPlotter()

    def set_bins(self, bins):
        self.traits.set_bins(bins)

    def contextMenuRequested(self, point):
        menu = QtGui.QMenu()
        axis_action = menu.addAction("reset axis limits")
        axis_action.triggered.connect(self.traits.reset_lims)
        # menu.addAction(self.autoscale_action)
        
        menu.exec_(self.mapToGlobal(point))

class PSTPlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    nreps = Int(DEFAULT_NREPS)
    bar_width = Float(0.005)

    def _plot_default(self):
        self.pst_data = ArrayPlotData(bins=[], spikecounts=[])
        plot = Plot(self.pst_data)
        plot.plot(('bins', 'spikecounts'), type='bar', name='PSTH', 
                    bar_width=self.bar_width)

        plot.value_range.low = 0
        plot.value_range.high = 30

        self.ax_zoom_tool = AxisZoomTool(plot, speed=0.1, single_axis=True,
                                   axis='index', maintain_aspect_ratio=False)
        plot.tools.append(self.ax_zoom_tool)
        plot.tools.append(PanTool(plot, constrain=True, constrain_direction='x', restrict_to_data=True))

        return plot


    def clear_data(self):
        """Clear histogram counts"""
        c = self.pst_data.get_data('spikecounts')
        c = np.zeros_like(c)
        self.pst_data.set_data('spikecounts', c)

    def set_bins(self, bins):
        counts = np.zeros_like(bins)
        self.pst_data.set_data('bins', bins)
        self.pst_data.set_data('spikecounts', counts)
        # set appropriate width of bars
        self.bar_width = bins[0]*1.5
        self.ax_zoom_tool.set_xdomain((0, bins[-1]))

    def append_data(self, bins, repnum=None):
        """Adds one to each bin index in list"""
        d = self.pst_data.get_data('spikecounts')
        for b in bins:
            d[b] += 1
        self.pst_data.set_data('spikecounts', d)

    def reset_lims(self):
        xdata = self.pst_data.get_data('bins')
        self.set_xlim((xdata[0],xdata[-1]))
        ydata = self.pst_data.get_data('spikecounts')
        self.set_ylim((0, ydata.max()))

    def set_xlim(self, lim):
        self.plot.index_range.low = lim[0]
        self.plot.index_range.high = lim[1]

    def set_ylim(self, lim):
        self.plot.value_range.low = lim[0]
        self.plot.value_range.high = lim[1]

    def _bar_width_changed(self):
        self.plot.components[0].bar_width = self.bar_width

class SpikePlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    nreps = Int(DEFAULT_NREPS)
    raster_ymax = Float(RASTER_YMAX)
    raster_ymin = Float(RASTER_YMIN)
    raster_yslots = np.linspace(RASTER_YMIN, RASTER_YMAX, DEFAULT_NREPS)
    threshold_val = 0.25
    tscale = 0.001 # ms
    signals = ProtocolSignals()
    
    def _plot_default(self):
        self.trace_data = ArrayPlotData(times=[], response=[], bins=[], spikes=[], 
                                        threshold=[self.threshold_val,self.threshold_val], 
                                        thresh_anchor=[])
        self.stim_data = ArrayPlotData(times=[], signal=[])

        trace_plot = Plot(self.trace_data)
        trace_plot.plot(('times', 'response'), type='line', name='response potential')
        trace_plot.plot(('bins', 'spikes'), type='scatter', name='detected spikes', color='black', marker_size=1.0)
        thresh_line, = trace_plot.plot(('thresh_anchor', 'threshold'), type='line', color='red')
        # must manually set sort order on array for map_index to work
        trace_plot.datasources['thresh_anchor'].sort_order = "ascending"

        self.stim_plot_height = 20
        stim_plot = Plot(self.stim_data)
        stim_plot.plot(('times', 'signal'), type='line', 
                        name='stim signal', color='blue')
        stim_plot.set(resizable='h',
                      bounds=[600,self.stim_plot_height], 
                      border_visible=False,
                      overlay_border=False)

        bare_axes(stim_plot)

        trace_plot.x_axis.title = 'Time (ms)'
        trace_plot.y_axis.title = 'voltage (mV)'
        self.default_tick_formatter = trace_plot.x_axis.tick_label_formatter
        trace_plot.x_axis.tick_label_formatter = self._time_ticks

        trace_plot.padding_bottom = 35
        trace_plot.padding_top = 0
        stim_plot.padding_top = 0
        stim_plot.padding_bottom = 0

        # Attach some tools to the plot
        broadcaster = SpikeTraceBroadcasterTool(thresh_line)
        broadcaster.tools.append(PanTool(trace_plot, constrain=True, constrain_direction='y'))
        broadcaster.tools.append(ZoomTool(trace_plot, axis='value', zoom_factor=1.1))
        linetool = LineDraggingTool(thresh_line)
        broadcaster.tools.append(linetool)
        trace_plot.tools.append(broadcaster)

        # setting the offsets after adding tools, sets it for all child tools
        broadcaster.set_offsets(trace_plot.padding_left, trace_plot.padding_bottom)
        linetool.register_signal(self.signals.threshold_updated)
        self.signals.threshold_updated.connect(self._update_thresh_data)

        # link x-axis ranges
        trace_plot.index_range = stim_plot.index_range

        # make sure side padding matches, or else time will be off
        trace_plot.padding_right = RIGHT_MARGIN
        stim_plot.padding_right = trace_plot.padding_right

        container = OverlayPlotContainer()
        # self.plot = container
        container.add(trace_plot)
        container.add(stim_plot)

        container.bgcolor = "transparent"
        self.trace_plot = trace_plot
        self.stim_plot = stim_plot

        return container

    def update_data(self, data, axeskey, datakey):
        if axeskey == 'stim':
            self.stim_data.set_data(datakey, data)
        if axeskey == 'response':
            self.trace_data.set_data(datakey, data)

    def clear_data(self, axeskey, datakey):
        if axeskey == 'response':
            self.trace_data.set_data(datakey, [])

    def append_data(self, data, axeskey, datakey):
        if axeskey == 'response':
            if datakey == 'spikes':
                # adjust repetition number to response scale
                data = np.ones_like(data)*self.raster_yslots[data[0]]
            d = self.trace_data.get_data(datakey)
            d = append(d, data)
            self.trace_data.set_data(datakey, d)

    def set_xlim(self, lim):
        self.trace_plot.index_range.low = lim[0]
        self.trace_plot.index_range.high = lim[1]
        self.trace_data.set_data('thresh_anchor', lim)

    def set_ylim(self, lim):
        self.trace_plot.value_range.low = lim[0]
        self.trace_plot.value_range.high = lim[1]

    def reset_lims(self):
        xdata = self.trace_data.get_data('times')
        self.set_xlim((xdata[0],xdata[-1]))
        ydata = self.trace_data.get_data('response')
        self.set_ylim((ydata.min(), ydata.max()))

    def set_tscale(self, scale):
        self.tscale = scale
        if self.tscale == 0.001:
            self.trace_plot.x_axis.title = 'Time (ms)'
        elif self.tscale == 1:
            self.trace_plot.x_axis.title = 'Time (s)'
        else:
            raise Exception(u"Invalid time scale")

    def _update_thresh_data(self, threshold):
        # manual drag does not update datasource, so do so here
        self.trace_data.set_data('threshold', [threshold, threshold])

    def _time_ticks(self, num):
        num = num/self.tscale
        return self.default_tick_formatter(num)

    def _noticks(self,num):
        return ''

    def _nreps_changed(self):
        self.raster_yslots = np.linspace(self.raster_ymin, self.raster_ymax, self.nreps)

    def _raster_ymax_changed(self):
        self.raster_yslots = np.linspace(self.raster_ymin, self.raster_ymax, self.nreps)

    def _raster_ymin_changed(self):
        self.raster_yslots = np.linspace(self.raster_ymin, self.raster_ymax, self.nreps)

class LinePlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    tscale = 0.001

    def _plot_default(self):
        self.line_data = ArrayPlotData(times=[], y=[])
        plot = Plot(self.fft_data)
        plot.plot(('times', 'y'), type='line')

        plot.x_axis.title = 'Time (ms)'
        plot.y_axis.title = 'voltage (mV)'

        self.default_tick_formatter = trace_plot.x_axis.tick_label_formatter
        plot.x_axis.tick_label_formatter = self._time_ticks

        plot.tools.append(PanTool(plot, constrain=True, constrain_direction='y'))
        plot.tools.append(ZoomTool(plot, axis='value', zoom_factor=1.1))

        return plot

    def update_data(self, key, value):
        self.line_data.set_data(key, value)

    def reset_lims(self):
        xdata = self.trace_data.get_data('times')
        self.set_xlim((xdata[0],xdata[-1]))
        ydata = self.trace_data.get_data('y')
        self.set_ylim((ydata.min(), ydata.max()))

    def set_tscale(self, scale):
        self.tscale = scale
        if self.tscale == 0.001:
            self.trace_plot.x_axis.title = 'Time (ms)'
        elif self.tscale == 1:
            self.trace_plot.x_axis.title = 'Time (s)'
        else:
            raise Exception(u"Invalid time scale")

    def _time_ticks(self, num):
        num = num/self.tscale
        return self.default_tick_formatter(num)

class FFTPlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    fscale = 1000
    freq_title = 'Frequency (kHz)'
    def _plot_default(self):
        self.fft_data = ArrayPlotData(freq=[], fft=[])
        plot = Plot(self.fft_data)
        plot.plot(('freq', 'fft'), type='line', name='Stimulus spectrum')
        plot.orientation = 'v'

        plot.x_axis.title = 'Intensity'
        plot.y_axis.title = self.freq_title

        self.default_tick_formatter = plot.y_axis.tick_label_formatter
        plot.y_axis.tick_label_formatter = self._freq_ticks

        plot.padding_left = 50
        plot.padding_right = 10
        plot.padding_bottom = 35
        plot.padding_top = 5

        plot.tools.append(PanTool(plot))
        plot.overlays.append(RectZoomTool(plot, always_on=False, always_on_modifier='control', 
                                          axis='value', zoom_factor=1.1))

        return plot

    def update_data(self, freq, fft):
        self.fft_data.set_data('freq', freq)
        self.fft_data.set_data('fft', fft)

    def reset_lims(self):
        index = self.fft_data.get_data('freq')
        self.plot.index_range.low = index[0]
        self.plot.index_range.high = index[-1]
        value = self.fft_data.get_data('fft')
        self.plot.value_range.low = value.min()
        self.plot.value_range.high = value.max()

    def set_fscale(self, scale):
        self.fscale = scale
        if self.fscale == 1000:
            self.freq_title = u'Frequency (kHz)'
        elif self.fscale == 1:
            self.freq_title = u'Frequency (Hz)'
        else:
            raise Exception(u"Invalid frequency scale")
        if self.plot.orientation == 'v':
            self.plot.y_axis.title = self.freq_title
        else:
            self.plot.x_axis.title = self.freq_title

    def set_orientation(self, orientation):
        self.plot.orientation = orientation
        if orientation == 'h':
            self.plot.x_axis.title = self.freq_title
            self.plot.y_axis.title = 'Intensity'
            self.plot.x_axis.tick_label_formatter = self._freq_ticks
            self.plot.y_axis.tick_label_formatter = self.default_tick_formatter
        elif orientation == 'v':
            self.plot.x_axis.title = 'Intensity'
            self.plot.y_axis.title = self.freq_title
            self.plot.y_axis.tick_label_formatter = self._freq_ticks
            self.plot.x_axis.tick_label_formatter = self.default_tick_formatter

    def _freq_ticks(self, num):
        num = num/self.fscale
        return self.default_tick_formatter(num)

class ImagePlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    fscale = 1000
    tscale = 0.001
    img_args = {'cmap': default_colormaps.jet}
    def _plot_default(self):
        self.img_data = ArrayPlotData()
        self.img_data.set_data('imagedata', np.zeros((5,5)))
        plot = Plot(self.img_data)
        p = plot.img_plot('imagedata', name="spectrogram", colormap=self.img_args['cmap'])

        self.default_tick_formatter = plot.y_axis.tick_label_formatter
        plot.y_axis.tick_label_formatter = self._freq_ticks
        plot.x_axis.tick_label_formatter = self._time_ticks
        
        plot.padding_top = 5
        plot.padding_bottom = 5
        plot.padding_right = RIGHT_MARGIN

        plot.overlays.append(ZoomTool(plot))

        self.cimage = p[0]
        return plot

    def update_data(self, imgdata, xaxis=None, yaxis=None):
        self.img_data.set_data('imagedata',imgdata)
        if xaxis is not None and yaxis is not None:
            self.cimage.index.set_data(xaxis, yaxis)
        self.cimage.request_redraw()

    def set_xlim(self, lim):
        self.plot.range2d.x_range.low = lim[0]
        self.plot.range2d.x_range.high = lim[1]

    def set_colormap(self, cmap_name):
        cmap = default_colormaps.color_map_name_dict[cmap_name]
        self.img_args['cmap'] = cmap
        self.cimage.value_mapper = cmap(self.cimage.color_mapper.range)
        self.cimage.request_redraw()

    def set_title(self, title):
        # make space for a title
        self.plot.padding_top = 25
        self.plot.overlays.append(PlotLabel(title,
                      component=self.plot,
                      font = "swiss 16",
                      overlay_position="top"))
        self.plot.padding_bottom = 35
        self.plot.x_axis.tick_visible = True
        self.set_tscale(self.tscale)
        self.set_fscale(self.fscale)
        
    def set_fscale(self, scale):
        self.fscale = scale
        if self.fscale == 1000:
            self.plot.y_axis.title = u'Frequency (kHz)'
        elif self.fscale == 1:
            self.plot.y_axis.title = u'Frequency (Hz)'
        else:
            raise Exception(u"Invalid frequency scale")
            
    def set_tscale(self, scale):
        self.tscale = scale
        if self.plot.x_axis.tick_visible:
            if self.tscale == 0.001:
                self.plot.x_axis.title = 'Time (ms)'
            elif self.tscale == 1:
                self.plot.x_axis.title = 'Time (s)'
            else:
                raise Exception(u"Invalid time scale")

    def _freq_ticks(self, num):
        num = num/self.fscale
        return self.default_tick_formatter(num)

    def _time_ticks(self, num):
        num = num/self.tscale
        return self.default_tick_formatter(num)


class ScrollingPlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    deltax = Float(1.0)
    windowsize = Float(10.0)
    def _plot_default(self):
        self.chart_data = ArrayPlotData(x=[], response=[], stim=[])
        response_plot = Plot(self.chart_data)
        response_plot.plot(('x', 'response'), type='line', name='chart')

        response_plot.range2d.x_range.low = 0
        response_plot.range2d.x_range.high = 1

        response_plot.x_axis.title = 'Time (s)'
        response_plot.y_axis.title = 'voltage (mV)'
        
        self.stim_plot_height = 20
        stim_plot = Plot(self.chart_data)
        stim_plot.plot(('x', 'stim'), type='line', name='chart')
        stim_plot.set(resizable='h',
                      bounds=[600,self.stim_plot_height], 
                      border_visible=False,
                      overlay_border=False)
        bare_axes(stim_plot)

        stim_plot.index_range = response_plot.index_range

        response_plot.tools.append(PanTool(response_plot))
        response_plot.tools.append(ZoomTool(response_plot, axis='value'))
        
        container = OverlayPlotContainer()

        container.add(response_plot)
        container.add(stim_plot)

        # container.bgcolor = "transparent"
        self.response_plot = response_plot
        self.stim_plot = stim_plot

        return container

    def set_time_delta(self, delta):
        self.deltax = delta

    def set_windowsize(self, winsz):
        self.windowsize = winsz
        self.response_plot.range2d.x_range.high = self.response_plot.range2d.x_range.low + winsz

    def append_data(self, stim, data):
        npoints_to_add = len(data)
        xdata = self.chart_data.get_data('x')
        if len(xdata) == 0:
            last_time = 0
        else:
            last_time = xdata[-1]

        # print 'last_time', last_time, 'deltax', self.deltax, 'npoints_to_add', npoints_to_add
        x_to_append = np.arange(last_time+self.deltax, 
                                last_time+self.deltax+(self.deltax*npoints_to_add),
                                self.deltax)
        xdata = np.append(xdata, x_to_append)

        ydata = self.chart_data.get_data('response')
        ydata = np.append(ydata, data)        
        stimdata = self.chart_data.get_data('stim')
        stimdata = np.append(stimdata, stim)

        # remove data that has gone off screen
        xlow = self.response_plot.range2d.x_range.low
        removex, = np.where(xdata < xlow)

        xdata = np.delete(xdata, removex)
        ydata = np.delete(ydata, removex)
        stimdata = np.delete(stimdata, removex)

        self.chart_data.set_data('x', xdata)
        self.chart_data.set_data("response", ydata)
        self.chart_data.set_data("stim", stimdata)

        # now scroll axis limits
        if self.response_plot.range2d.x_range.high < xdata[-1]:
            self.response_plot.range2d.x_range.high += self.deltax*npoints_to_add
            self.response_plot.range2d.x_range.low += self.deltax*npoints_to_add


def bare_axes(plot):
    plot.x_axis.axis_line_visible = False
    plot.x_axis.tick_visible = False
    plot.y_axis.tick_visible = False
    plot.x_axis.tick_label_formatter = _noticks
    plot.y_axis.tick_label_formatter = _noticks
    plot.y_grid.visible = False

def _noticks(num):
    return ''

if __name__ == '__main__':
    import os
    import spikeylab.tools.audiotools as audiotools
    import test.sample as sample

    app = QtGui.QApplication(sys.argv)

    sylpath = sample.samplewav()
    spec, f, bins, fs = audiotools.spectrogram(sylpath)

    # spec_plot = SpecWidget()
    # spec_plot.update_data(spec, xaxis=bins, yaxis=f)
    # spec_plot.show()

    psth = PSTHWidget()
    psth.set_bins(range(10))
    psth.append_data([0, 1, 1, 1, 3, 4, 4,9,9,9,9,9, 7], 0)
    psth.resize(800, 400)
    psth.show()

    sys.exit(app.exec_())
