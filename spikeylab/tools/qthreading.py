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

class GenericObject(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    def __init__(self, function, *args, **kwargs):
        QtCore.QObject.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def process(self):
        try:
            self.function(*self.args,**self.kwargs)
        except:
            self.error.emit("There was an error :(")
        self.finished.emit()
        
class Thread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

     # this class is solely needed for these two methods, there
     # appears to be a bug in PyQt 4.6 that requires you to
     # explicitly call run and start from the subclass in order
     # to get the thread to actually start an event loop

    def start(self):
        QtCore.QThread.start(self)

    def run(self):
        QtCore.QThread.run(self)

class SimpleObject(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    def process(self):
        try:
            print "Hello its me!"
        except:
            self.error.emit("There was an error :(")
        self.finished.emit()

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