from PyQt4 import QtGui, QtCore

from spikeylab.gui.plotting.protocoldisplay import ProtocolDisplay
from spikeylab.gui.plotting.calibration_display import CalibrationDisplay
from spikeylab.gui.plotting.calibration_explore_display import ExtendedCalibrationDisplay
from spikeylab.gui.plotting.pyqtgraph_widgets import ChartWidget
from spikeylab.gui.plotmenubar import PlotMenuBar

class PlotDockWidget(QtGui.QDockWidget):
    def __init__(self, parent=None):
        super(PlotDockWidget, self).__init__(parent)
        
        self.topLevelChanged.connect(self.floatingStuff)
        self.displays = {'calibration': CalibrationDisplay(), 
                         'standard':ProtocolDisplay(), 
                         'calexp': ExtendedCalibrationDisplay(),
                         'chart': ChartWidget()}
        self.setWidget(self.displays['standard'])
        self._current = 'standard'

        self.setTitleBarWidget(PlotMenuBar(self))

    def floatingStuff(self, floating):
        if floating:
            self.setWindowFlags(QtCore.Qt.Window)
            self.setVisible(True) # not sure why this is necessary
        else:
            self.setWindowFlags(QtCore.Qt.Widget)

    def switchDisplay(self, display):
        if display in self.displays:
            self.setWidget(self.displays[display])
            self._current = display
        else:
            raise Exception("Undefined display type "+ display)

    def current(self):
        return self._current