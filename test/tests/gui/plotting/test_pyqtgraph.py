import inspect
import os
import sys
import time

import numpy as np
import sip
from nose.tools import assert_equal
from numpy.testing import assert_array_almost_equal, assert_array_equal

import robouser
import sparkle.tools.audiotools as audiotools
import test.sample as sample
from sparkle.QtWrapper.QtCore import Qt, QTimer
from sparkle.QtWrapper.QtGui import QApplication
from sparkle.gui.plotting.pyqtgraph_widgets import ChartWidget, FFTWidget, \
    ProgressWidget, PSTHWidget, SimplePlotWidget, SpecWidget, StackedPlot, \
    TraceWidget

sip.setdestroyonexit(0)

PAUSE = 0.0

def data_func(f):
    t = np.arange(200)
    return t, 2*np.sin(2*np.pi*f*t/len(t))

class TestFFTWidget():
    def setUp(self):
        self.fig = FFTWidget()
        self.fig.show()

    def tearDown(self):
        self.fig.close()
        QApplication.closeAllWindows()
        QApplication.processEvents()

    def test_fft_plot(self):
        self.fig.setWindowTitle(inspect.stack()[0][3])
        for i in range(1,5):
            t, y = data_func(i)
            self.fig.updateData(t*1000, y) # gets integer divided by 1000
            QApplication.processEvents()
            time.sleep(PAUSE)

    def test_widget_rotation(self):
        assert self.fig.getLabel('left') == 'Frequency (Hz)'
        assert self.fig.getLabel('bottom') == ''
        fig1 = FFTWidget(rotation=0)
        assert fig1.getLabel('left') == ''
        assert fig1.getLabel('bottom') == 'Frequency (Hz)'
        fig1.close()

class TestTraceWidget():
    def setUp(self):
        self.fig = TraceWidget()
        self.fig.show()

    def tearDown(self):
        self.fig.close()
        QApplication.closeAllWindows()
        QApplication.processEvents()

    def test_threshold(self):
        self.fig.setThreshold(0.33)
        assert self.fig.getThreshold() == 0.33

    def test_raster_bounds(self):
        self.fig.setRasterBounds((0.1, 0.4))
        assert self.fig.getRasterBounds() == (0.1, 0.4)

    def test_ask_raster_bounds(self):
        QTimer.singleShot(1000, lambda : robouser.keypress('enter'))
        self.fig.askRasterBounds()

    def test_spike(self):
        self.fig.setWindowTitle(inspect.stack()[0][3])
        self.fig.setThreshold(0.5)
        for i in range(1,5):
            t, y = data_func(i)
            self.fig.updateData(axeskey='response', x=t, y=y)
            self.fig.autoRange()
            QApplication.processEvents()
            time.sleep(PAUSE)

    def test_raster(self):
        self.fig.setNreps(5)
        self.fig.setWindowTitle(inspect.stack()[0][3])

        acq_rate = 50000
        nbins=20
        bin_centers = np.linspace(0,float(20000)/acq_rate, nbins)
        dummy_bins = bin_centers[0:-1:2]
        dummy_data = np.ones_like(dummy_bins)
        self.fig.appendData('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        dummy_bins = bin_centers[1:-2:2]
        dummy_data = np.ones_like(dummy_bins)*2
        self.fig.appendData('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        dummy_bins = bin_centers[1:-2:2]
        dummy_data = np.ones_like(dummy_bins)*3
        self.fig.appendData('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

    def test_stim(self):
        self.fig.setWindowTitle(inspect.stack()[0][3])
        for i in range(1,5):
            t, y = data_func(i)
            self.fig.updateData(axeskey='stim', x=t, y=y)
            self.fig.autoRange()
            QApplication.processEvents()
            time.sleep(PAUSE)

class TestSpecWidget():
    def setUp(self):
        self.fig = SpecWidget()
        self.fig.show()

    def tearDown(self):
        self.fig.close()
        QApplication.closeAllWindows()
        QApplication.processEvents()

    def test_spec_plot(self):
        self.fig.setWindowTitle(inspect.stack()[0][3])
        assert not self.fig.hasImg()
        for i in range(1,5):
            t, y = data_func(i)
            self.fig.updateData(y, 32)
            QApplication.processEvents()
            time.sleep(PAUSE)
            assert self.fig.hasImg()

        self.fig.clearImg()
        assert not self.fig.hasImg()

    def test_set_spec_args(self):
        specargs = {u'nfft':256, u'window':u'blackman', u'overlap':50,
                    'colormap' :{'lut':None, 'state':None, 'levels':None}}
        self.fig.setSpecArgs(**specargs)
        assert_equal(self.fig.getColormap(), specargs['colormap'])

    def test_cmap_editor(self):
        before = self.fig.getColormap().copy()
        self.fig.editColormap()
        assert_equal(self.fig.getColormap(), before)
        self.fig.editor.close()

class TestSimplePlotWidget():
    def setUp(self):
        self.fig = SimplePlotWidget([],[])
        self.fig.show()

    def tearDown(self):
        self.fig.close()
        QApplication.closeAllWindows()
        QApplication.processEvents()

    def test_simple_plot(self):
        self.fig.setWindowTitle(inspect.stack()[0][3])
        for i in range(1,5):
            t, y = data_func(i)
            self.fig.appendData(t, y)
            self.fig.autoRange()
            QApplication.processEvents()
            time.sleep(PAUSE)
        plot_items = self.fig.listDataItems()
        assert len(plot_items) == 5

    def test_labels(self):
        self.fig.setLabels('x label', 'y label', 'mytitle', 'X', 'Y')
        assert self.fig.getLabel('bottom') == 'x label (X)'
        assert self.fig.getLabel('left') == 'y label (Y)'
        assert self.fig.getPlotItem().titleLabel.text == 'mytitle'

    def test_2d_yvals(self):
        x = np.arange(10)
        y = np.ones((2,10))
        y[1,:] = y[1,:]*2
        fig = SimplePlotWidget(x,y)

        plot_items = fig.listDataItems()
        assert len(plot_items) == 2

        fig.close()

class TestProgressWidget():
    def setUp(self):
        self.xs = range(10)
        self.ys = range(3)
        self.fig = ProgressWidget(self.ys, (self.xs[0], self.xs[-1]))
        self.fig.show()

    def tearDown(self):
        self.fig.close()
        QApplication.closeAllWindows()
        QApplication.processEvents()
        
    def test_progress_plots(self):
        self.fig.setWindowTitle(inspect.stack()[0][3])
        for y in self.ys:
            for x in self.xs:
                self.fig.setPoint(x, y, y*2)
                QApplication.processEvents()
                time.sleep(PAUSE/4)

        for y in self.ys:
            xvals, yvals = self.fig.lines[y].getData()
            assert_array_equal(yvals, np.ones_like(self.xs)*y*2)

    def test_label(self):
        self.fig.setLabels('calibration')
        assert self.fig.getLabel('bottom') == 'Frequency (Hz)'
        assert self.fig.getPlotItem().titleLabel.text == 'Calibration Curve'
        self.fig.setLabels('tuning')
        assert self.fig.getLabel('bottom') == 'Frequency (Hz)'
        assert self.fig.getPlotItem().titleLabel.text == 'Tuning Curve'
        self.fig.setLabels(None)
        print 'bottom label', self.fig.getLabel('bottom')
        assert self.fig.getLabel('bottom') == 'Test Number '
        assert self.fig.getPlotItem().titleLabel.text == 'Spike Counts'

class TestPSTHWidget():
    def test_psth_widget(self):
        fig = PSTHWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()

        dummy_data = np.array([0,1,1,1,3,4,4,9,9,9,9,9,7])
        nbins = max(dummy_data)+1
        fig.setBins(range(nbins))
        fig.appendData(dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        control_data = []
        for bin_num in range(nbins):
            control_data.append(len(dummy_data[dummy_data == bin_num]))
        barvals = fig.getData()
        assert_array_equal(barvals, control_data)

        for i in range(3):
            fig.appendData(np.array([3, 3, 4, 5]))
            control_data[3] += 2
            control_data[4] += 1
            control_data[5] += 1
            QApplication.processEvents()
            time.sleep(PAUSE)

        barvals = fig.getData()
        assert_array_equal(barvals, control_data)

        fig.clearData()
        barvals = fig.getData()
        assert_array_equal(barvals, np.zeros(nbins))

        fig.close()
        QApplication.closeAllWindows()
        QApplication.processEvents()

class TestStackedWidget():
    def setup(self):
        self.fig = StackedPlot()
        self.fig.setWindowTitle(inspect.stack()[0][3])
        self.fig.show()

    def teardown(self):
        self.fig.close()
        QApplication.closeAllWindows()
        QApplication.processEvents()

    def test_stacking_plots(self):
        for i in range(1,5):
            t, y = data_func(i)
            self.fig.addPlot(t, y)
            self.fig.addSpectrogram(y, 100)
            QApplication.processEvents()
            time.sleep(PAUSE)

        # flip through plots?
        assert self.fig.stacker.currentIndex() == 0
        self.fig.nextPlot()
        assert self.fig.stacker.currentIndex() == 1
        self.fig.prevPlot()
        assert self.fig.stacker.currentIndex() == 0
        self.fig.lastPlot()
        assert self.fig.stacker.currentIndex() == 7
        self.fig.firstPlot()
        assert self.fig.stacker.currentIndex() == 0

class TestOtherWidgets():
    def test_chart_widget(self):
        fig = ChartWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()
        winsz = 0.01 #seconds
        acq_rate = 50000 #Hz
        fig.setWindowSize(winsz)
        fig.setSr(acq_rate)
        for i in range(1,5):
            t, y = data_func(i)
            fig.appendData(y,y)
            QApplication.processEvents()
            time.sleep(PAUSE)
        fig.close()
        QApplication.closeAllWindows()
        QApplication.processEvents()
