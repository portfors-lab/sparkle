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

class ProtocolSignals(QtCore.QObject):
    curve_finished = QtCore.pyqtSignal()
    ncollected = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    warning = QtCore.pyqtSignal(str)
    response_collected = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    calibration_response_collected = QtCore.pyqtSignal(tuple, numpy.ndarray, numpy.ndarray, float, float)
    current_trace = QtCore.pyqtSignal(int, int, dict)
    current_rep = QtCore.pyqtSignal(int)
    spikes_found = QtCore.pyqtSignal(list, int)
    stim_generated = QtCore.pyqtSignal(numpy.ndarray, int)
    threshold_updated = QtCore.pyqtSignal(float)
    trace_finished = QtCore.pyqtSignal(int, float, float, float)
    group_finished = QtCore.pyqtSignal(bool)
    calibration_file_changed = QtCore.pyqtSignal(str)
    tuning_curve_started = QtCore.pyqtSignal(list, list, str)
    tuning_curve_response = QtCore.pyqtSignal(int, int, float)

class TestSignals(QtCore.QObject):
    update_data = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    done = QtCore.pyqtSignal()