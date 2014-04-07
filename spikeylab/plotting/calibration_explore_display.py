from PyQt4 import QtGui, QtCore

from spikeylab.plotting.pyqtgraph_widgets import TraceWidget, SpecWidget, FFTWidget

class ExtendedCalibrationDisplay(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.stim_fft_plot = FFTWidget(self, rotation=0)
        self.response_fft_plot = FFTWidget(self, rotation=0)
        self.response_fft_plot.disableAutoRange()

        self.stim_fft_plot.set_title("Stimulus FFT")
        self.response_fft_plot.set_title("Response FFT")
        self.response_fft_plot.setXLink(self.stim_fft_plot)

        self.stim_signal_plot = FFTWidget(rotation=0)
        self.response_signal_plot = FFTWidget(rotation=0)
        self.response_signal_plot.disableAutoRange()
        self.stim_signal_plot.setLabel('left', 'Potential', units='V')
        self.response_signal_plot.setLabel('left', 'Potential', units='V')
        self.response_signal_plot.setLabel('bottom', 'Time', units='s')
        self.response_signal_plot.setMouseEnabled(x=False, y=True)
        self.stim_signal_plot.setMouseEnabled(x=False, y=True)
        self.response_signal_plot.set_title("Response Signal")
        self.stim_signal_plot.set_title("Stimulus Signal")
        self.stim_signal_plot.setXLink(self.response_signal_plot)

        self.stim_spec_plot = SpecWidget(self)
        self.response_spec_plot = SpecWidget(self)
        self.stim_spec_plot.setXLink(self.response_spec_plot)
        self.stim_spec_plot.setYLink(self.response_spec_plot)
        self.response_spec_plot.set_title("Response Spectrogram")
        self.stim_spec_plot.set_title("Stim Spectrogram")

        splitter_signal = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter_fft = QtGui.QSplitter(QtCore.Qt.Vertical)
        container_spec = QtGui.QWidget()
        container_signal = QtGui.QWidget()
        layout_spec = QtGui.QHBoxLayout()
        layout_spec.setContentsMargins(0,0,0,0)
        layout_signal = QtGui.QHBoxLayout()
        layout_signal.setContentsMargins(0,0,0,0)

        # splitter_signal.addWidget(self.stim_signal_plot)
        # splitter_signal.addWidget(self.response_signal_plot)
        layout_signal.addWidget(self.stim_signal_plot)
        layout_signal.addWidget(self.response_signal_plot)
        container_signal.setLayout(layout_signal)
        splitter_fft.addWidget(self.stim_fft_plot)
        splitter_fft.addWidget(self.response_fft_plot)
        layout_spec.addWidget(self.stim_spec_plot)
        layout_spec.addWidget(self.response_spec_plot)
        container_spec.setLayout(layout_spec)

        splitter_left = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter_main = QtGui.QSplitter(QtCore.Qt.Vertical)

        splitter_left.addWidget(container_spec)
        splitter_left.addWidget(container_signal)
        splitter_main.addWidget(splitter_left)
        splitter_main.addWidget(splitter_fft)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitter_main)
        self.setLayout(layout)

        # splitter_fft.setSizes()
        print 'windowsize', 
        height = self.size().height()
        splitter_left.setSizes([height*0.3, height*0.1])
        splitter_main.setSizes([height*0.4, height*0.6])

        self.colormap_changed = self.stim_spec_plot.colormap_changed
        self.colormap_changed = self.response_spec_plot.colormap_changed

    def set_spec_args(self, *args, **kwargs):
        self.stim_spec_plot.set_spec_args(*args, **kwargs)
        self.response_spec_plot.set_spec_args(*args, **kwargs)

    def update_spec(self, *args, **kwargs):
        if args[0] == None:
            self.stim_spec_plot.clear_img()
            self.response_spec_plot.clear_img()
        else:
            p = kwargs.pop('plot')
            if p == 'response':
                self.response_spec_plot.update_data(*args, **kwargs)
            else:
                self.stim_spec_plot.update_data(*args, **kwargs)

    def update_signal(self, *args, **kwargs):
        p = kwargs.pop('plot')
        if p == 'response':
            self.response_signal_plot.update_data(*args, **kwargs)
        else:
            self.stim_signal_plot.update_data(*args, **kwargs)

    def update_fft(self, *args, **kwargs):
        p = kwargs.pop('plot')
        if p == 'response': 
            self.response_fft_plot.update_data(*args, **kwargs)
        else:
            self.stim_fft_plot.update_data(*args, **kwargs)

    def set_xlimits(self, lims):
        self.response_signal_plot.set_xlim(lims)
        self.stim_signal_plot.set_xlim(lims)

    def auto_range(self):
        self.response_signal_plot.autoRange()
        self.response_fft_plot.autoRange()