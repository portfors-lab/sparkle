from PyQt4 import QtCore, QtGui

from tcform import Ui_TuningCurve

class TuningCurve(QtGui.QWidget):
    def __init__(self, outchans, inchans, parent=None):
        # auto generated code intialization
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_TuningCurve()
        self.ui.setupUi(self)

        # assume one channel each for now
        self.aochan = outchans
        self.aichan = inchans

        self.ui.start_btn.clicked.connect(self.run_curve)
        self.ui.stop_btn.clicked.connect(self.abort_curve)

    def run_curve(self):
        print "run curve"

    def abort_curve(self):
        print "abort!"

