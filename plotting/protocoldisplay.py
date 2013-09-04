import sys

from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"
from enthought.chaco.api import GridPlotContainer

from audiolab.plotting.chacoplots import ImagePlotter, Plotter, DataPlotWidget, ImageWidget

from PyQt4 import QtGui, QtCore

class ProtocolDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.spec_plot = ImageWidget(self)
        # self.fft_plot = Plotter(self, 1, rotation = -90)
        self.fft_plot = DataPlotWidget(rotation=-90)
        self.spiketrace_plot = DataPlotWidget(self)
        self.signal_plot = DataPlotWidget(self)

        # container = GridPlotContainer(shape=(3,2))
        # container.insert(0, self.spec_plot)
        # container.insert(2, self.signal_plot)
        # container.insert(4, self.spiketrace_plot)
        # container.insert(5, self.fft_plot)


        self.signal_plot.setMinimumHeight(100)
        self.spec_plot.setMinimumHeight(100)
        self.spiketrace_plot.setMinimumWidth(500)
        self.spiketrace_plot.setMinimumHeight(500)
        self.fft_plot.setMinimumWidth(100)
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

        splitternw.addWidget(self.spec_plot)
        splitternw.addWidget(self.signal_plot)
        splittersw.addWidget(splitternw)
        splitternw.addWidget(self.spiketrace_plot)
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

    def set_xlimits(self, lims):
        self.spec_plot.set_xlim(lims)
        self.signal_plot.set_xlim(lims)
        self.spiketrace_plot.set_xlim(lims)

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
    y = random.randint(0,10) * np.sin(x)
    plot.update_signal(x,y)
    plot.update_spiketrace(x,y)
    for i in range(10):
        y = random.randint(0,10) * np.sin(x)
        plot.update_fft(x,y)
        time.sleep(0.2)
        QtGui.QApplication.processEvents()


    sys.exit(app.exec_())