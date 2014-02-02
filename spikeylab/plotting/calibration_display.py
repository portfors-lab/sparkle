import sys
import numpy as np

from enthought.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from spikeylab.plotting.custom_plots import FFTWidget

from PyQt4 import QtGui, QtCore

class CalibrationDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.out_fft = FFTWidget(self)
        self.in_fft = FFTWidget(self)
        self.out_fft.traits.set_orientation('h')
        self.in_fft.traits.set_orientation('h')
        self.out_fft.traits.plot.title = "Output Tone FFT"
        self.in_fft.traits.plot.title = "Input Tone FFT"
        self.in_fft.traits.plot.padding_top = 50
        self.out_fft.traits.plot.padding_top = 50
        self.in_fft.traits.plot.padding_left = 60
        self.out_fft.traits.plot.padding_left = 60

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        splitter.addWidget(self.out_fft)
        splitter.addWidget(self.in_fft)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def update_out_fft(self, *args, **kwargs):
        self.out_fft.update_data(*args, **kwargs)

    def update_in_fft(self, *args, **kwargs):
        self.in_fft.update_data(*args, **kwargs)

    def set_fscale(self, scale):
        self.out_fft.traits.set_fscale(scale)
        self.in_fft.traits.set_fscale(scale)