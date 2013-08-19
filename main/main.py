import sys, os

from PyQt4 import QtCore, QtGui

from audiolab.io.daq_tasks import *

from audiolab.config.info import caldata_filename, calfreq_filename
from mainform import Ui_ChoicesWindow
from tuning_curve_gui import TuningCurve

class ChoicesWindow(QtGui.QMainWindow):
    def __init__(self, dev_name, parent=None):
        # auto generated code intialization
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_ChoicesWindow()
        self.ui.setupUi(self)

        cnames = get_ao_chans(dev_name.encode())
        self.ui.aochan_box.addItems(cnames)
        cnames = get_ai_chans(dev_name.encode())
        self.ui.aichan_box.addItems(cnames)

        self.ui.curve_btn.clicked.connect(self.do_curve)
        self.ui.chart_btn.clicked.connect(self.do_chart)
        self.ui.experiment_btn.clicked.connect(self.do_experiment)
        self.ui.explore_btn.clicked.connect(self.do_explore)

    def do_explore(self):
        print "explore function"

    def do_curve(self):
        aochan = str(self.ui.aochan_box.currentText())
        aichan = str(self.ui.aichan_box.currentText())

        tcwidget = TuningCurve(aochan,aichan)
        tcwidget.show()
        self.current_work_window = tcwidget

    def do_chart(self):
        pass

    def do_experiment(self):
        pass

    def launch_calibration_dlg(self):
        pass

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    devName = "PCI-6259"
    myapp = ChoicesWindow(devName)
    myapp.show()
    sys.exit(app.exec_())
