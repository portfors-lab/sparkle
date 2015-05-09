import numpy

from sparkle.QtWrapper import QtCore


class ProtocolSignals(QtCore.QObject):
    curve_finished = QtCore.Signal()
    ncollected = QtCore.Signal(numpy.ndarray, numpy.ndarray)
    warning = QtCore.Signal(str)
    response_collected = QtCore.Signal(numpy.ndarray, numpy.ndarray, int, int, int, dict)
    average_response = QtCore.Signal(int, int, float)
    calibration_response_collected = QtCore.Signal(numpy.ndarray, numpy.ndarray, float)
    current_trace = QtCore.Signal(int, int, dict)
    current_rep = QtCore.Signal(int)
    spikes_found = QtCore.Signal(list, int)
    stim_generated = QtCore.Signal(numpy.ndarray, int)
    threshold_updated = QtCore.Signal(float)
    trace_finished = QtCore.Signal(int, float, float, float)
    group_finished = QtCore.Signal(bool)
    calibration_file_changed = QtCore.Signal(str)
    tuning_curve_started = QtCore.Signal(list, list, str)
    tuning_curve_response = QtCore.Signal(int, object, float)
    over_voltage = QtCore.Signal(float)

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
    update_data = QtCore.Signal(numpy.ndarray, numpy.ndarray)
    done = QtCore.Signal()
