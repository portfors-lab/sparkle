from PyQt4 import QtCore
import numpy

class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
    """
    def __del__(self):
        self.wait()
    """
    def run(self):
        self.function(*self.args,**self.kwargs)
        return

class BaseSignals(QtCore.QObject):
    curve_finished = QtCore.pyqtSignal()
    ncollected = QtCore.pyqtSignal(numpy.ndarray)

class CalibrationSignals(BaseSignals):
    stim_generated = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    spectrum_analyzed = QtCore.pyqtSignal(int, int, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    read_collected = QtCore.pyqtSignal(int, int, numpy.ndarray)
    ncollected = QtCore.pyqtSignal(list)

class ProtocolSignals(BaseSignals):
    response_collected = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    spikes_found = QtCore.pyqtSignal(list, list)
    stim_generated = QtCore.pyqtSignal(tuple, numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    threshold_updated = QtCore.pyqtSignal(float)
    trace_finished = QtCore.pyqtSignal()

class TestSignals(QtCore.QObject):
    update_data = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    done = QtCore.pyqtSignal()