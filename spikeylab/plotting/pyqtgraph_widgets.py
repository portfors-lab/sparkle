from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

from spikeylab.dialogs.raster_bounds_dlg import RasterBoundsDialog

STIM_HEIGHT = 0.10

## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class TraceWidget(QtGui.QWidget):
    nreps = 20
    raster_ymin = 0.5
    raster_ymax = 1
    raster_yslots = np.linspace(raster_ymin, raster_ymax, nreps)
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.pw = pg.PlotWidget(name='trace')
        self.trace_plot = self.pw.plot(pen='k')
        self.raster_plot = self.pw.plot(pen=None, symbol='s', symbolPen=None, symbolSize=4, symbolBrush='k')
        self.thresh_line = self.pw.plot(pen='r')
        self.stim_plot = self.pw.plot(pen='b')

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.pw)
        self.setLayout(layout)

        self.pw.sigRangeChanged.connect(self.range_change)
        self.pw.sigScaleChanged.connect(self.scale_change)

        self.pw.disableAutoRange()
        self.pw.setMouseEnabled(x=False,y=True)

        # print 'scene', self.pw.scene().contextMenu[0].text()
        # print 'scene', self.trace_plot.scene().contextMenu[0].text()
        # # self.pw.scene().contextMenu = []
        # print 'items', 
        # for act in self.pw.getPlotItem().ctrlMenu.actions():
        #     print act.text()
        # print '-'*20
        # for act in self.pw.getPlotItem().vb.menu.actions():
        #     print act.text()
        # print '-'*20
        # because of pyqtgraph internals, we can't just remove action from menu
        self.fake_action = QtGui.QAction("", None)
        self.pw.getPlotItem().vb.menu.leftMenu = self.fake_action
        self.fake_action.setCheckable(True)
        self.pw.getPlotItem().vb.menu.mouseModes = [self.fake_action]

        raster_bounds_action = QtGui.QAction("edit raster bounds", None)
        self.pw.scene().contextMenu.append(raster_bounds_action) #should use function for this?
        raster_bounds_action.triggered.connect(self.ask_raster_bounds)

    def update_data(self, axeskey, **kwargs):
        if axeskey == 'stim':
            self.stim_plot.setData(**kwargs)
            # call manually to ajust placement of signal
            ranges = self.pw.viewRange()
            self.range_change(self.pw, ranges)
        if axeskey == 'response':
            self.trace_plot.setData(**kwargs)
            if 'x' in kwargs:
                # Consider changing to calling this explicitly on window size change
                self._update_threshold_anchor()

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
        self.pw.setXRange(*lim)

    def set_ylim(self, lim):
        self.pw.setYRange(*lim)

    def get_threshold(self):
        x, y = self.tresh_line.getData()
        return y[0]

    def set_threshold(self, threshold):
        x, y = self.trace_plot.getData()
        if x is not None:
            trace_lims = [x[0], x[-1]]
        else:
            trace_lims = [0, 0]    
        self.thresh_line.setData(x=trace_lims, y=[threshold, threshold])

    def _update_threshold_anchor(self):
        x, y = self.trace_plot.getData()
        if x is not None:
            a, threshold = self.thresh_line.getData()
            trace_lims = [x[0], x[-1]]
            self.thresh_line.setData(x=trace_lims, y=threshold)

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

    def set_tscale(self, tscale):
        pass

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

    def scale_change(self, obj):
        print 'scale change', obj