from PyQt4 import QtGui, QtCore

class PlotMenuBar(QtGui.QMenuBar):
    def __init__(self, dock, parent=None):
        super(PlotMenuBar, self).__init__(parent)

        standardAction = QtGui.QAction('standard', self)
        calibrationAction = QtGui.QAction('calibration', self)
        calExpAction = QtGui.QAction('calibration explore', self)
        standardAction.triggered.connect(lambda: self.switch_display('standard'))
        calibrationAction.triggered.connect(lambda: self.switch_display('calibration'))
        calExpAction.triggered.connect(lambda: self.switch_display('calexp'))

        viewMenu = self.addMenu('View')
        viewMenu.addAction(standardAction)
        viewMenu.addAction(calibrationAction)
        viewMenu.addAction(calExpAction)

        self.dock = dock

    def switch_display(self, display):
        self.dock.switch_display(display)

    def mousePressEvent(self, event):
        if event.x() < 50:
            super(PlotMenuBar, self).mousePressEvent(event)
        else:
            # ignore to allow proper functioning of float
            event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()