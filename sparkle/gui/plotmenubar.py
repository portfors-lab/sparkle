from sparkle.QtWrapper import QtGui


class PlotMenuBar(QtGui.QMenuBar):
    """Menu bar for the plot dock widget"""
    def __init__(self, dock, parent=None):
        super(PlotMenuBar, self).__init__(parent)

        standardAction = QtGui.QAction('standard', self)
        calibrationAction = QtGui.QAction('calibration', self)
        calExpAction = QtGui.QAction('calibration explore', self)
        standardAction.triggered.connect(lambda: self.switchDisplay('standard'))
        calibrationAction.triggered.connect(lambda: self.switchDisplay('calibration'))
        calExpAction.triggered.connect(lambda: self.switchDisplay('calexp'))

        viewMenu = self.addMenu('View')
        viewMenu.addAction(standardAction)
        viewMenu.addAction(calibrationAction)
        viewMenu.addAction(calExpAction)

        self.dock = dock

    def switchDisplay(self, display):
        """See :meth:`PlotDockWidget<sparkle.gui.plotdock.PlotDockWidget.switchDisplay>`"""
        self.dock.switchDisplay(display)

    def mousePressEvent(self, event):
        """Marshalls behaviour depending on location of the mouse click"""
        if event.x() < 50:
            super(PlotMenuBar, self).mousePressEvent(event)
        else:
            # ignore to allow proper functioning of float
            event.ignore()

    def mouseMoveEvent(self, event):
        """Passes event on to allow dragging of window"""
        event.ignore()

    def mouseReleaseEvent(self, event):
        """Passes event on to allow dragging of window"""
        event.ignore()
