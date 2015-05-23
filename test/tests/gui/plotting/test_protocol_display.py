import sys
import time

import numpy as np

from sparkle.QtWrapper.QtGui import QApplication
from sparkle.gui.plotting.protocoldisplay import ProtocolDisplay
from test.sample import samplewav

PAUSE = 0

    
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

        QApplication.processEvents()

        display.clearRaster()

        time.sleep(PAUSE)

        display.close()

    def test_multiple_recordings_display(self):

        display = ProtocolDisplay('chan0')
        display.show()

        display.addResponsePlot('chan1', 'chan2')

        display.setNreps(5)
        data = self.data_func(3)

        display.updateSpiketrace(self.t, data, 'chan0')
        display.updateSpiketrace(self.t, data, 'chan1')
        display.updateSpiketrace(self.t, data, 'chan2')

        # check range matching
        lims = [0.11, 0.66]
        display.responsePlots['chan1'].setXlim(lims)

        # print 'lims', lims, display.responsePlots['chan0'].viewRange()[0], display.responsePlots['chan2'].viewRange()[0], display.specPlot.viewRange()[0]
        assert lims == display.responsePlots['chan0'].viewRange()[0] \
                    == display.responsePlots['chan2'].viewRange()[0] \
                    == display.specPlot.viewRange()[0]

    def test_add_remove_plots(self):

        display = ProtocolDisplay('chan0')
        display.show()

        display.addResponsePlot('chan1', 'chan2')
        assert display.responsePlotCount() == 3

        display.removeResponsePlot('chan1', 'chan2')
        assert display.responsePlotCount() == 1

        display.addResponsePlot('chan1')
        assert display.responsePlotCount() == 2

        display.removeResponsePlot('chan0', 'chan1')
        assert display.responsePlotCount() == 0
        
    def test_remove_non_existant_plot(self):

        display = ProtocolDisplay('chan0')
        display.show()

        display.removeResponsePlot('chan1')
        assert display.responseNameList() == ['chan0']