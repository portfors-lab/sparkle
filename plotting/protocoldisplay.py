import sys

from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"
from enthought.chaco.api import GridPlotContainer

from audiolab.plotting.chacoplots import ImagePlotter, Plotter

from PyQt4 import QtGui, QtCore

class ProtocolDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.spec_plot = ImagePlotter(self)
        self.fft_plot = Plotter(self, 1, rotation = -90)
        self.spiketrace_plot = Plotter(self,1)
        self.signal_plot = Plotter(self,1)

        # container = GridPlotContainer(shape=(3,2))
        # container.insert(0, self.spec_plot)
        # container.insert(2, self.signal_plot)
        # container.insert(4, self.spiketrace_plot)
        # container.insert(5, self.fft_plot)

        self.spiketrace_plot.widget.setMinimumWidth(500)
        self.fft_plot.widget.setMinimumWidth(100)
        self.fft_plot.widget.setMinimumHeight(400)

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
        splitterse.addWidget(self.fft_plot.widget)

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


if __name__ == "__main__":
    import random
    import numpy as np
    app = QtGui.QApplication(sys.argv)
    plot = ProtocolDisplay()
    plot.resize(800, 400)
    plot.show()

    x = np.arange(200)
    y = random.randint(0,10) * np.sin(x)
    plot.update_spiketrace(x,y)

    sys.exit(app.exec_())