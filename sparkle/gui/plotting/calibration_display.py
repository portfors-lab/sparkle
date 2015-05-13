from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.plotting.pyqtgraph_widgets import FFTWidget


class CalibrationDisplay(QtGui.QWidget):
    """Widget container with two FFT plots, of outgoing and incoming signal,
    intending for use with calibration operation"""
    def __init__(self, parent=None):
        super(CalibrationDisplay, self).__init__(parent)

        self.outFft = FFTWidget(self, rotation=0)
        self.inFft = FFTWidget(self, rotation=0)
        self.outFft.setTitle("Output Tone FFT (To Speaker)")
        self.inFft.setTitle("Input Tone FFT (From Microphone)")
        self.outFft.setLabel('bottom', 'Frequency', units='Hz')
        self.outFft.setLabel('left', '', units='')
        self.inFft.setLabel('bottom', 'Frequency', units='Hz')
        self.inFft.setLabel('left', '', units='')

        self.inFft.enableAutoRange(x=True, y=False)
        self.outFft.enableAutoRange(x=True, y=False)
        self.inFft.setRange(yRange=(0,100))
        self.outFft.setRange(yRange=(0,100))

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        splitter.addWidget(self.outFft)
        splitter.addWidget(self.inFft)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def updateOutFft(self, *args, **kwargs):
        """Sets new data for outgoing FFT

        for arguments, see :meth:`FFTWidget.updateData<sparkle.gui.plotting.pyqtgraph_widgets.FFTWidget.updateData>`
        """
        self.outFft.updateData(*args, **kwargs)

    def updateInFft(self, *args, **kwargs):
        """Sets new data for recorded FFT

        for arguments, see :meth:`FFTWidget.updateData<sparkle.gui.plotting.pyqtgraph_widgets.FFTWidget.updateData>`
        """
        self.inFft.updateData(*args, **kwargs)
