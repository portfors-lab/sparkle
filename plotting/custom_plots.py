import sys
from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from traits.api import HasTraits, Instance, List
from traitsui.api import View, Item
from chaco.api import Plot, ArrayPlotData, OverlayPlotContainer
from enable.component_editor import ComponentEditor
from enthought.enable.api import Window
from chaco.tools.api import PanTool, ZoomTool
from enthought.chaco.tools.rect_zoom import RectZoomTool

import numpy as np
from scipy.special import jn

from PyQt4 import QtCore, QtGui

LEFT_MARGIN = 50
RIGHT_MARGIN = 10
FREQ_UNIT = 1000

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

    def set_xlim(self, *args, **kwargs):
        self.traits.set_xlim(*args, **kwargs)


class FFTWidget(BaseWidget):
    def _create_plotter(self):
        return FFTPlotter()

    def contextMenuRequested(self, point):
        menu = QtGui.QMenu()
        traits_action = menu.addAction("reset axis limits")
        traits_action.triggered.connect(self.traits.reset_lims)
        menu.exec_(self.mapToGlobal(point))

class TraceWidget(BaseWidget):
    def _create_plotter(self):
        return SpikePlotter()
    
    def resizeEvent(self, event):
        tp_bounds = self.traits.trace_plot.bounds
        # print 'trace plot', self.traits.trace_plot.position, tp_bounds
        # print 'stim plot', self.traits.stim_plot.position
        self.traits.stim_plot.set(position=[50,tp_bounds[1]-self.traits.stim_plot_height]) 

    def contextMenuRequested(self, point):
        menu = QtGui.QMenu()
        traits_action = menu.addAction("reset axis limits")
        traits_action.triggered.connect(self.traits.reset_lims)
        menu.exec_(self.mapToGlobal(point))

class SpecWidget(BaseWidget):
    def _create_plotter(self):
        return ImagePlotter()

class SpikePlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    # trace_data = ArrayPlotData
    # times_index = Array
    # response_data = Array
    # spike_data = Array

    # def __init__(self):
    
    def _plot_default(self):
        self.trace_data = ArrayPlotData(times=[], response=[], bins=[], spikes=[])
        self.stim_data = ArrayPlotData(times=[], signal=[])

        #create a LinePlot instance and add it to the subcontainer
        # trace_plot = create_line_plot([index, value], add_grid=True,
        #                         add_axis=True, index_sort='ascending')
        # raster_plot = create_scatter_plot([index, value])

        trace_plot = Plot(self.trace_data)
        trace_plot.plot(('times', 'response'), type='line', name='response potential')
        trace_plot.plot(('bins', 'spikes'), type='scatter', name='detected spikes')
        trace_plot.set(bounds=[600,500], position=[0,0])

        self.stim_plot_height = 20
        stim_plot = Plot(self.stim_data)
        stim_plot.plot(('times', 'signal'), type='line', 
                        name='stim signal', color='blue')
        stim_plot.set(resizable='h',
                      bounds=[600,self.stim_plot_height], 
                      position=[50,350], 
                      border_visible=False,
                      overlay_border=False)
        stim_plot.y_axis.orientation = "right"
        stim_plot.x_axis.axis_line_visible = False
        stim_plot.x_axis.tick_visible = False
        stim_plot.x_axis.tick_label_formatter = self._noticks
        stim_plot.y_grid.visible = False

        trace_plot.x_axis.title = 'Time (s)'
        trace_plot.y_axis.title = 'voltage (mV)'

        trace_plot.tools.append(PanTool(trace_plot))
        trace_plot.tools.append(ZoomTool(trace_plot))

        # link x-axis ranges
        trace_plot.index_range = stim_plot.index_range

        trace_plot.padding_bottom = 40
        trace_plot.padding_top = 0

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
            self.trace_data.set_data(datakey, []])

    def append_data(self, data, axeskey, datakey):
        if axeskey == 'response':
            d = self.trace_data.get_data(datakey)
            d.append(data)
            self.trace_data.set_data(datakey, data)

    def set_xlim(self, lim):
        self.trace_plot.index_range.low = lim[0]
        self.trace_plot.index_range.high = lim[1]

    def set_ylim(self, lim):
        self.trace_plot.value_range.low = lim[0]
        self.trace_plot.value_range.high = lim[1]

    def reset_lims(self):
        xdata = self.trace_data.get_data('times')
        self.set_xlim((xdata[0],xdata[-1]))
        ydata = self.trace_data.get_data('response')
        self.set_ylim((ydata.min(), ydata.max()))

    def _noticks(self,num):
        return ''

class FFTPlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    def _plot_default(self):
        self.fft_data = ArrayPlotData(freq=[], fft=[])
        plot = Plot(self.fft_data)
        plot.plot(('freq', 'fft'), type='line', name='Stimulus spectrum')
        plot.orientation = 'v'

        plot.x_axis.title = 'Intensity'
        plot.y_axis.title = 'Frequency (kHz)'

        plot.padding_left = 50
        plot.padding_right = 10
        plot.padding_bottom = 40
        plot.padding_top = 0

        plot.overlays.append(RectZoomTool(plot))

        return plot

    def update_data(self, freq, fft):
        freq = freq/FREQ_UNIT
        self.fft_data.set_data('freq', freq)
        self.fft_data.set_data('fft', fft)

    def reset_lims(self):
        index = self.fft_data.get_data('freq')
        self.plot.index_range.low = index[0]
        self.plot.index_range.high = index[-1]
        value = self.fft_data.get_data('fft')
        self.plot.value_range.low = value.min()
        self.plot.value_range.high = value.max()

class ImagePlotter(HasTraits):
    plot = Instance(OverlayPlotContainer)
    def _plot_default(self):
        self.img_data = ArrayPlotData()
        self.img_data.set_data('imagedata', np.zeros((5,5)))
        plot = Plot(self.img_data)
        plot.img_plot('imagedata', name="spectrogram")

        plot.padding_top = 0
        plot.padding_bottom = 20
        plot.padding_right = RIGHT_MARGIN

        plot.overlays.append(ZoomTool(plot))

        return plot

    def update_data(self, imgdata, xaxis=None, yaxis=None):
        self.img_data.set_data('imagedata',imgdata)
        if xaxis is not None and yaxis is not None:
            yaxis = yaxis/FREQ_UNIT
            self.plot.components[0].index.set_data(xaxis, yaxis)
        self.plot.components[0].request_redraw()

    def set_xlim(self, lim):
        self.plot.range2d.x_range.low = lim[0]
        self.plot.range2d.x_range.high = lim[1]

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    qt_container = QtContainer()
    qt_container.show()
    qt_container.resize(1000,600)
    sys.exit(app.exec_())
