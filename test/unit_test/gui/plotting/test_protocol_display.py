import sys
import time

from PyQt4.QtGui import QApplication
import numpy as np

from spikeylab.gui.plotting.protocoldisplay import ProtocolDisplay
from test.sample import samplewav

PAUSE = 0

app = None
def setUp():
    global app
    app = QApplication(sys.argv)

def tearDown():
    global app
    app.exit(0)
    
class TestProtocolDisplay():

    def setUp(self):
        self.t = np.arange(200)

    def data_func(self, f):
        return 2*np.sin(2*np.pi*f*self.t/len(self.t))

    def test_display(self):
        display = ProtocolDisplay()
        display.show()

        display.setNreps(5)

        display.updateSpec(samplewav())
        display.specAutoRange()
        QApplication.processEvents()
        assert display.specPlot.hasImg()
        time.sleep(PAUSE)
        display.updateSpec(None)
        QApplication.processEvents()
        assert not display.specPlot.hasImg()
        time.sleep(PAUSE)
        display.showSpec(samplewav())
        QApplication.processEvents()
        assert display.specPlot.hasImg()

        data = self.data_func(3)
        nbins = 50
        bin_centers = np.linspace(0, self.t[-1], nbins)
        points = np.ones(nbins)

        display.updateSignal(self.t, data)
        display.updateSpiketrace(self.t, data)
        display.updateFft(self.t, data)
        display.addRasterPoints(bin_centers, points)
        display.addRasterPoints(bin_centers, points*2)

        display.setXlimits((self.t[0], self.t[-1]))
        display.setTscale(0.001)
        display.setFscale(1000)

        QApplication.processEvents()

        display.clearRaster()

        time.sleep(PAUSE)

        display.close()