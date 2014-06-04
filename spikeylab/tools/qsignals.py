from PyQt4 import QtCore
import numpy

class ProtocolSignals(QtCore.QObject):
    curve_finished = QtCore.pyqtSignal()
    ncollected = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    warning = QtCore.pyqtSignal(str)
    response_collected = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    average_response = QtCore.pyqtSignal(int, int, float)
    calibration_response_collected = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray, float)
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
    over_voltage = QtCore.pyqtSignal(float)

class TestSignals(QtCore.QObject):
    update_data = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    done = QtCore.pyqtSignal()