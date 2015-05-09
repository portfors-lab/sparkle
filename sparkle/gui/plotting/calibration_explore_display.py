from sparkle.QtWrapper import QtCore, QtGui
from sparkle.gui.plotting.pyqtgraph_widgets import FFTWidget, SpecWidget, \
    TraceWidget


class ExtendedCalibrationDisplay(QtGui.QWidget):
    """Display Widget for intended for use with calibration operation with 
    plots for signal, FFT, and spectrogram of output and incoming signals"""
    def __init__(self, parent=None):
        super(ExtendedCalibrationDisplay, self).__init__(parent)

        self.stimFftPlot = FFTWidget(self, rotation=0)
        self.responseFftPlot = FFTWidget(self, rotation=0)
        self.responseFftPlot.disableAutoRange()

        self.stimFftPlot.setTitle("Stimulus FFT")
        self.responseFftPlot.setTitle("Response FFT")
        self.responseFftPlot.setXLink(self.stimFftPlot)

        self.stimFftPlot.enableAutoRange(x=True, y=False)
        self.responseFftPlot.enableAutoRange(x=True, y=False)
        self.stimFftPlot.setRange(yRange=(0,100))
        self.responseFftPlot.setRange(yRange=(0,100))

        self.stimSignalPlot = FFTWidget(rotation=0)
        self.responseSignalPlot = FFTWidget(rotation=0)
        self.responseSignalPlot.disableAutoRange()
        self.responseSignalPlot.setRange(yRange=(-0.1,0.1))
        self.stimSignalPlot.setLabel('left', 'Potential', units='V')
        self.responseSignalPlot.setLabel('left', 'Potential', units='V')
        self.responseSignalPlot.setLabel('bottom', 'Time', units='s')
        self.responseSignalPlot.setMouseEnabled(x=False, y=True)
        self.stimSignalPlot.setMouseEnabled(x=False, y=True)
        self.responseSignalPlot.setTitle("Response Signal")
        self.stimSignalPlot.setTitle("Stimulus Signal")
        self.stimSignalPlot.setXLink(self.responseSignalPlot)

        self.stimSpecPlot = SpecWidget(self)
        self.responseSpecPlot = SpecWidget(self)
        self.stimSpecPlot.setXLink(self.responseSpecPlot)
        self.stimSpecPlot.setYLink(self.responseSpecPlot)
        self.responseSpecPlot.setTitle("Response Spectrogram")
        self.stimSpecPlot.setTitle("Stim Spectrogram")

        splitterSignal = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterFft = QtGui.QSplitter(QtCore.Qt.Vertical)
        containerSpec = QtGui.QWidget()
        containerSignal = QtGui.QWidget()
        layoutSpec = QtGui.QHBoxLayout()
        layoutSpec.setContentsMargins(0,0,0,0)
        layoutSignal = QtGui.QHBoxLayout()
        layoutSignal.setContentsMargins(0,0,0,0)

        # splitterSignal.addWidget(self.stimSignalPlot)
        # splitterSignal.addWidget(self.responseSignalPlot)
        layoutSignal.addWidget(self.stimSignalPlot)
        layoutSignal.addWidget(self.responseSignalPlot)
        containerSignal.setLayout(layoutSignal)
        splitterFft.addWidget(self.stimFftPlot)
        splitterFft.addWidget(self.responseFftPlot)
        layoutSpec.addWidget(self.stimSpecPlot)
        layoutSpec.addWidget(self.responseSpecPlot)
        containerSpec.setLayout(layoutSpec)

        splitterLeft = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterMain = QtGui.QSplitter(QtCore.Qt.Vertical)

        splitterLeft.addWidget(containerSpec)
        splitterLeft.addWidget(containerSignal)
        splitterMain.addWidget(splitterLeft)
        splitterMain.addWidget(splitterFft)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitterMain)
        self.setLayout(layout)

        # splitterFft.setSizes()
        height = self.size().height()
        splitterLeft.setSizes([height*0.3, height*0.1])
        splitterMain.setSizes([height*0.4, height*0.6])

        self.colormapChanged = self.stimSpecPlot.colormapChanged
        self.colormapChanged = self.responseSpecPlot.colormapChanged

    # def setSpecArgs(self, *args, **kwargs):
    #     """Sets the parameters for the spectrogram calculation/drawing,
    #     chosen by the user.

    #     For arguments, see: :meth:`SpecWidget.setSpecArgs<sparkle.gui.plotting.pyqtgraph_widgets.SpecWidget.setSpecArgs>`
    #     """
    #     self.stimSpecPlot.setSpecArgs(*args, **kwargs)
    #     self.responseSpecPlot.setSpecArgs(*args, **kwargs)

    def updateSpec(self, *args, **kwargs):
        """Updates the spectrogram given by kwarg *'plot'*, which is
        either 'response' or (well actually anything). If no arguments 
        are given, clears both spectrograms.

        For other arguments, see: :meth:`SpecWidget.updateData<sparkle.gui.plotting.pyqtgraph_widgets.SpecWidget.updateData>`
        """
        if args[0] is None:
            self.stimSpecPlot.clearImg()
            self.responseSpecPlot.clearImg()
        else:
            p = kwargs.pop('plot')
            if p == 'response':
                self.responseSpecPlot.updateData(*args, **kwargs)
            else:
                self.stimSpecPlot.updateData(*args, **kwargs)

    def updateSignal(self, *args, **kwargs):
        """Updates the signal plots kwarg *'plot'*, which is
        either 'response' or (well actually anything).

        For other arguments, see: :meth:`FFTWidget.updateData<sparkle.gui.plotting.pyqtgraph_widgets.FFTWidget.updateData>`
        """
        p = kwargs.pop('plot')
        if p == 'response':
            self.responseSignalPlot.updateData(*args, **kwargs)
        else:
            self.stimSignalPlot.updateData(*args, **kwargs)

    def updateFft(self, *args, **kwargs):
        """Updates the FFT plots kwarg *'plot'*, which is
        either 'response' or (well actually anything).

        For other arguments, see: :meth:`FFTWidget.updateData<sparkle.gui.plotting.pyqtgraph_widgets.FFTWidget.updateData>`
        """
        p = kwargs.pop('plot')
        if p == 'response': 
            self.responseFftPlot.updateData(*args, **kwargs)
        else:
            self.stimFftPlot.updateData(*args, **kwargs)

    def setXlimits(self, lims):
        """Sets the X axis limits of the signal plots

        :param lims: (min, max) of x axis, in same units as data
        :type lims: (float, float)
        """
        self.responseSignalPlot.setXlim(lims)
        self.stimSignalPlot.setXlim(lims)

    def autoRange(self):
        """Automatically adjust the visiable region of the response
        signal and FFT plots"""
        self.responseSignalPlot.autoRange()
        self.responseFftPlot.autoRange()

if __name__ == "__main__":
    import random, time, os, sys
    import numpy as np
    import sparkle.tools.audiotools as audiotools
    import scipy.io.wavfile as wv
    import test.sample as sample
    from scipy.io import loadmat
    import cProfile
    
    sylpath = sample.samplewav()
    fs, signal = audiotools.audioread(sylpath)
    signal = np.hstack((signal, signal))
    times = np.linspace(0,float(len(signal))/fs, len(signal))
    freq, spec = audiotools.calc_spectrum(signal, fs)

    app = QtGui.QApplication(sys.argv)

    profiler = cProfile.Profile()
    profiler.enable()
    
    plot = ExtendedCalibrationDisplay()
    plot.showMaximized()

    plot.updateSpec(signal, fs, plot='response')
    plot.updateSpec(signal, fs, plot='stim')

    plot.updateFft(freq, spec, plot='response')
    plot.updateFft(freq, spec, plot='stim')

    plot.updateSignal(times, signal, plot='response')
    plot.updateSignal(times, signal, plot='stim')
    
    profiler.disable()
    profiler.dump_stats('caldisplay.profile')

    sys.exit(app.exec_())
