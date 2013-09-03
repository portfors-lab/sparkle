import sys

from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"
from enthought.chaco.api import GridPlotContainer

from audiolab.plotting.chacoplots import ImagePlotter, Plotter, DataPlotWidget

from PyQt4 import QtGui, QtCore

class ProtocolDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.spec_plot = ImagePlotter(self)
        # self.fft_plot = Plotter(self, 1, rotation = -90)
        self.fft_plot = DataPlotWidget(rotation=-90)
        self.spiketrace_plot = Plotter(self,1)
        self.signal_plot = Plotter(self,1)

        # container = GridPlotContainer(shape=(3,2))
        # container.insert(0, self.spec_plot)
        # container.insert(2, self.signal_plot)
        # container.insert(4, self.spiketrace_plot)
        # container.insert(5, self.fft_plot)

        self.spiketrace_plot.widget.setMinimumWidth(500)
        self.fft_plot.setMinimumWidth(200)
        self.fft_plot.setMinimumHeight(100)

        # layout = QtGui.QGridLayout()
        # # layout.setSpacing(10)
        # layout.addWidget(self.spec_plot.widget, 0, 0)
        # layout.addWidget(self.signal_plot.widget, 1, 0)
        # layout.addWidget(self.spiketrace_plot.widget, 2, 0)
        # layout.addWidget(self.fft_plot.widget, 2, 1)

        splittersw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitternw = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterse = QtGui.QSplitter(QtCore.Qt.Horizontal)

        splitternw.addWidget(self.spec_plot.widget)
        splitternw.addWidget(self.signal_plot.widget)
        splittersw.addWidget(splitternw)
        splitternw.addWidget(self.spiketrace_plot.widget)
        splitterse.addWidget(splitternw)
        # splitterse.addWidget(RotatableView(self.fft_plot))
        splitterse.addWidget(self.fft_plot)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(splitterse)
        self.setLayout(layout)


    def update_spec(self, *args, **kwargs):
        self.spec_plot.update_data(*args, **kwargs)

    def update_fft(self, *args, **kwargs):
        self.fft_plot.update_data(*args, **kwargs)

    def update_spiketrace(self, *args, **kwargs):
        self.spiketrace_plot.update_data(*args, **kwargs)

    def update_signal(self, *args, **kwargs):
        self.signal_plot.update_data(*args, **kwargs)

class RotatableView(QtGui.QGraphicsView):
    def __init__(self, item, rotation=0):
        QtGui.QGraphicsView.__init__(self)
        scene = QtGui.QGraphicsScene(self)
        self.setScene(scene)
        graphics_item = scene.addWidget(item)
        graphics_item.rotate(rotation)
        self.item = graphics_item
        # make the QGraphicsView invisible
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("border: 0px")

    def resizeEvent(self,event):
        sz = event.size()
        self.item.setGeometry(QtCore.QRectF(0,0,sz.width(), sz.height()))

if __name__ == "__main__":
    import random, time
    import numpy as np
    app = QtGui.QApplication(sys.argv)
    plot = ProtocolDisplay()
    plot.resize(800, 400)
    plot.show()

    x = np.arange(200)
    for i in range(10):
        y = random.randint(0,10) * np.sin(x)
        plot.update_fft(x,y)
        time.sleep(0.2)
        QtGui.QApplication.processEvents()


    sys.exit(app.exec_())