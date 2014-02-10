import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
sip.setdestroyonexit(0)

from spikeylab.plotting.pyqtgraph_widgets import FFTWidget, \
        TraceWidget, SpecWidget

import sys, os, time
import inspect
import numpy as np

from PyQt4.QtGui import QApplication

import spikeylab.tools.audiotools as audiotools
import test.sample as sample

PAUSE = 0.5

app = None
def setUp():
    global app
    app = QApplication(sys.argv)

def tearDown():
    global app
    app.exit(0)


class TestPyqtgraphPlots():
    def setUp(self):
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
            QApplication.processEvents()
            time.sleep(PAUSE)

        fig.close()

    def test_trace_widget_spike(self):
        fig = TraceWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.set_threshold(0.5)
        fig.show()
        for i in range(1,5):
            y = self.data_func(i)
            fig.update_data(axeskey='response', x=self.t, y=y)
            fig.autoRange()
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
        fig.append_data('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        dummy_bins = bin_centers[1:-2:2]
        dummy_data = np.ones_like(dummy_bins)*2
        fig.append_data('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        dummy_bins = bin_centers[1:-2:2]
        dummy_data = np.ones_like(dummy_bins)*3
        fig.append_data('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        fig.close()

    def test_trace_widget_stim(self):
        fig = TraceWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()
        for i in range(1,5):
            y = self.data_func(i)
            fig.update_data(axeskey='stim', x=self.t, y=y)
            fig.autoRange()
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
