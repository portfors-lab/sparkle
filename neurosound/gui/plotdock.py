import time

from QtWrapper import QtGui, QtCore

from neurosound.gui.plotting.protocoldisplay import ProtocolDisplay
from neurosound.gui.plotting.calibration_display import CalibrationDisplay
from neurosound.gui.plotting.calibration_explore_display import ExtendedCalibrationDisplay
from neurosound.gui.plotting.pyqtgraph_widgets import ChartWidget
from neurosound.gui.plotmenubar import PlotMenuBar

class PlotDockWidget(QtGui.QDockWidget):
    """Widget that contains all of the data display widgets"""
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
        """Sets window flag appropriately when widget is floated/unfloated

        :param floating: whether the widget is now on its own
        :type floating: bool
        """
        pass # This causes the program to crash :(
        # if floating:
        #     self.setWindowFlags(QtCore.Qt.Window)
        #     self.setVisible(True) # not sure why this is necessary
        # else:
        #     self.setWindowFlags(QtCore.Qt.Widget)

    def switchDisplay(self, display):
        """Switches the visible widget to the one named *display*

        :param: the name of the desired display to show
        :type: str
        """
        if display in self.displays:
            self.setWidget(self.displays[display])
            self._current = display
        else:
            raise Exception("Undefined display type "+ display)

    def current(self):
        """Name of the currently shown display

        :returns: str -- name of widget displayed
        """
        return self._current