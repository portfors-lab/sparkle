import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
sip.setdestroyonexit(0)

from spikeylab.plotting.pyqtgraph_widgets import FFTWidget, \
        TraceWidget, SpecWidget, ProgressWidget, PSTHWidget, ChartWidget

import sys, os, time
import inspect
import numpy as np

from PyQt4.QtGui import QApplication

import spikeylab.tools.audiotools as audiotools
import test.sample as sample

PAUSE = 0.0

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
            fig.updateData(self.t*1000, y) # gets integer divided by 1000
            QApplication.processEvents()
            time.sleep(PAUSE)

        fig.close()

    def test_trace_widget_spike(self):
        fig = TraceWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.setThreshold(0.5)
        fig.show()
        for i in range(1,5):
            y = self.data_func(i)
            fig.updateData(axeskey='response', x=self.t, y=y)
            fig.autoRange()
            QApplication.processEvents()
            time.sleep(PAUSE)

        fig.close()

    def test_trace_widget_raster(self):
        fig = TraceWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.setNreps(5)
        fig.show()

        acq_rate = 50000
        nbins=20
        bin_centers = np.linspace(0,float(20000)/acq_rate, nbins)
        dummy_bins = bin_centers[0:-1:2]
        dummy_data = np.ones_like(dummy_bins)
        fig.appendData('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        dummy_bins = bin_centers[1:-2:2]
        dummy_data = np.ones_like(dummy_bins)*2
        fig.appendData('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        dummy_bins = bin_centers[1:-2:2]
        dummy_data = np.ones_like(dummy_bins)*3
        fig.appendData('raster', dummy_bins, dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        fig.close()

    def test_trace_widget_stim(self):
        fig = TraceWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()
        for i in range(1,5):
            y = self.data_func(i)
            fig.updateData(axeskey='stim', x=self.t, y=y)
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
            fig.updateData(y, 32)
            QApplication.processEvents()
            time.sleep(PAUSE)
            
        fig.close()

    def test_progress_widget(self):
        xs = range(10)
        ys = range(3)
        fig = ProgressWidget(xs, ys)
        fig.show()
        for y in ys:
            for x in xs:
                fig.setPoint(x, y, y*2)
                QApplication.processEvents()
                time.sleep(PAUSE/4)

        fig.close()

    def test_psth_widget(self):
        fig = PSTHWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()

        dummy_data = [0, 1, 1, 1, 3, 4, 4,9,9,9,9,9, 7]
        fig.setBins(range(max(dummy_data)+1))
        fig.appendData(dummy_data)
        QApplication.processEvents()
        time.sleep(PAUSE)

        for i in range(3):
            fig.appendData([3, 3, 4, 5])

            QApplication.processEvents()
            time.sleep(PAUSE)

        fig.clearData()

        fig.close()

    def test_chart_widget(self):
        fig = ChartWidget()
        fig.setWindowTitle(inspect.stack()[0][3])
        fig.show()
        winsz = 0.01 #seconds
        acq_rate = 50000 #Hz
        fig.setWindowSize(winsz)
        fig.setSr(acq_rate)
        for i in range(1,5):
            y = self.data_func(i)
            fig.appendData(y,y)
            QApplication.processEvents()
            time.sleep(PAUSE)
        fig.close()
