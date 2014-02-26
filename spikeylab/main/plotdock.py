from PyQt4 import QtGui, QtCore

from spikeylab.plotting.protocoldisplay import ProtocolDisplay
from spikeylab.plotting.calibration_display import CalibrationDisplay
from spikeylab.plotting.calibration_explore_display import ExtendedCalibrationDisplay
from spikeylab.main.plotmenubar import PlotMenuBar

class PlotDockWidget(QtGui.QDockWidget):
    def __init__(self, parent=None):
        super(PlotDockWidget, self).__init__(parent)
        self.topLevelChanged.connect(self.floatingStuff)
        self.displays = {'calibration': CalibrationDisplay(), 'standard':ProtocolDisplay(), 'calexp': ExtendedCalibrationDisplay()}
        self.setWidget(self.displays['standard'])

        self.setTitleBarWidget(PlotMenuBar(self))

    def floatingStuff(self, floating):
        if floating:
            self.setWindowFlags(QtCore.Qt.Window)
            self.setVisible(True) # not sure why this is necessary
        else:
            self.setWindowFlags(QtCore.Qt.Widget)

    def switch_display(self, display):
        if display in self.displays:
            self.setWidget(self.displays[display])
        else:
            raise Exception("Undefined display type "+ display)