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

    def iteritems(self):
        return {
        'curve_finished' : self.curve_finished,
        'ncollected' : self.ncollected,
        'warning' : self.warning,
        'response_collected' : self.response_collected,
        'average_response' : self.average_response,
        'calibration_response_collected' : self.calibration_response_collected,
        'current_trace' : self.current_trace,
        'current_rep' : self.current_rep,
        'spikes_found' : self.spikes_found,
        'stim_generated' : self.stim_generated,
        'threshold_updated' : self.threshold_updated,
        'trace_finished' : self.trace_finished,
        'group_finished' : self.group_finished,
        'calibration_file_changed' : self.calibration_file_changed,
        'tuning_curve_started' : self.tuning_curve_started,
        'tuning_curve_response' : self.tuning_curve_response,
        'over_voltage' : self.over_voltage,
        }.iteritems()

class TestSignals(QtCore.QObject):
    update_data = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)
    done = QtCore.pyqtSignal()