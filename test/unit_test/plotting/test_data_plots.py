from spikeylab.plotting.custom_plots import FFTWidget, \
        TraceWidget, SpecWidget, PSTHWidget, ChartWidget

import sys, os, time
import inspect
import numpy as np

from PyQt4.QtGui import QApplication

import spikeylab.tools.audiotools as audiotools
import test.sample as sample

PAUSE = 0.5

class TestChacoPlots():
    """ Run through plotting data, and make sure no errors occur"""

    def setUp(self):
        self.app = QApplication(sys.argv)
        self.t = np.arange(200)

    def data_func(self, f):
        return 2*np.sin(2*np.pi*f*self.t/len(self.t))

    def test_fft_widget(self):
        fig = FFTWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()
        for i in range(1,5):
            y = self.data_func(i)
            fig.update_data(self.t*1000, y) # gets integer divided by 1000
            fig.traits.reset_lims()
            QApplication.processEvents()
            time.sleep(PAUSE)

        fig.close()

    def test_trace_widget_spike(self):
        fig = TraceWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.set_threshold(0.5)
        fig.show()
        fig.update_data(self.t, datakey='times', axeskey='response')
        for i in range(1,5):
            y = self.data_func(i)
            fig.update_data(y, datakey='response', axeskey='response')
            QApplication.processEvents()
            time.sleep(PAUSE)

        fig.close()

    def test_trace_widget_raster(self):
        fig = TraceWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.set_nreps(5)
        fig.show()

        acq_rate = 50000
        nbins=20
        bin_centers = np.linspace(0,float(20000)/acq_rate, nbins)
        dummy_bins = bin_centers[0:-1:2]
        dummy_data = np.ones_like(dummy_bins)
        fig.append_data(dummy_bins, 'response', 'bins')
        fig.append_data(dummy_data, 'response', 'spikes')
        QApplication.processEvents()
        time.sleep(PAUSE)

        dummy_bins = bin_centers[1:-2:2]
        dummy_data = np.ones_like(dummy_bins)*2
        fig.append_data(dummy_bins, 'response', 'bins')
        fig.append_data(dummy_data, 'response', 'spikes')
        QApplication.processEvents()
        time.sleep(PAUSE)

        dummy_bins = bin_centers[1:-2:2]
        dummy_data = np.ones_like(dummy_bins)*3
        fig.append_data(dummy_bins, 'response', 'bins')
        fig.append_data(dummy_data, 'response', 'spikes')
        QApplication.processEvents()
        time.sleep(PAUSE)

        fig.close()

    def test_trace_widget_stim(self):
        fig = TraceWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()
        fig.update_data(self.t, datakey='times', axeskey='stim')
        for i in range(1,5):
            y = self.data_func(i)
            fig.update_data(y, datakey='signal', axeskey='stim')
            QApplication.processEvents()
            time.sleep(PAUSE)

        fig.close()

    def test_spec_widget(self):
        fig = SpecWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()

        for i in range(1,5):
            y = self.data_func(i)
            fig.update_data(y, 32)
            QApplication.processEvents()
            time.sleep(PAUSE)
            
        fig.close()

    def test_psth_widget(self):
        fig = PSTHWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()

        dummy_data = [0, 1, 1, 1, 3, 4, 4,9,9,9,9,9, 7]
        fig.set_bins(range(len(dummy_data)))
        fig.append_data(dummy_data)

        QApplication.processEvents()
        time.sleep(PAUSE)

        fig.traits.reset_lims()
        fig.clear_data()

        fig.close()

    def test_chart_widget(self):
        fig = ChartWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()
        winsz = 0.01 #seconds
        acq_rate = 50000 #Hz
        fig.set_windowsize(winsz)
        fig.set_sr(acq_rate)
        for i in range(1,5):
            y = self.data_func(i)
            fig.append_data(y,y)
            QApplication.processEvents()
            time.sleep(PAUSE)
        fig.close()
