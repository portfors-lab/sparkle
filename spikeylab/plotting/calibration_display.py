import sys
import numpy as np

from spikeylab.plotting.pyqtgraph_widgets import FFTWidget

from PyQt4 import QtGui, QtCore

class CalibrationDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.out_fft = FFTWidget(self, rotation=0)
        self.in_fft = FFTWidget(self, rotation=0)
        self.out_fft.set_title("Output Tone FFT (To Speaker)")
        self.in_fft.set_title("Input Tone FFT (From Microphone)")
        self.out_fft.setLabel('bottom', 'Frequency', units='Hz')
        self.out_fft.setLabel('left', '', units='')
        self.in_fft.setLabel('bottom', 'Frequency', units='Hz')
        self.in_fft.setLabel('left', '', units='')

        self.in_fft.enableAutoRange(x=True, y=False)
        self.out_fft.enableAutoRange(x=True, y=False)
        self.in_fft.setRange(yRange=(0,100))
        self.out_fft.setRange(yRange=(0,100))

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
        self.out_fft.set_fscale(scale)
        self.in_fft.set_fscale(scale)