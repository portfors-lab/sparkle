from PyQt4 import QtCore
import numpy

class GenericThread(QtCore.QRunnable):
    def __init__(self, function, *args, **kwargs):
        QtCore.QRunnable.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
    u"""
    def __del__(self):
        self.wait()
    """
    def run(self):
        self.function(*self.args,**self.kwargs)
        return

class WorkerSignals(QtCore.QObject):
    done = QtCore.pyqtSignal(int, int, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    curve_finished = QtCore.pyqtSignal()
    update_stim_display = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    ncollected = QtCore.pyqtSignal(list)
    read_collected = QtCore.pyqtSignal(int, int, numpy.ndarray)

class TestSignals(QtCore.QObject):
    update_data = QtCore.pyqtSignal(numpy.ndarray, numpy.ndarray)