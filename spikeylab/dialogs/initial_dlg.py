from PyQt4 import QtGui
from initialform import Ui_InitialDlg

class InitialDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_InitialDlg()
        self.ui.setupUi(self)

    def browse(self):
        if self.ui.new_radio.isChecked():
            fname = QtGui.QFileDialog.getSaveFileName(self, u"Create New File",
                                    filter="data files(*.hdf5 *.h5)")
        elif self.ui.prev_radio.isChecked():
            fname = QtGui.QFileDialog.getOpenFileName(self, "Append to Existing Data File", 
                                    filter="data files(*.hdf5 *.h5)")
        if fname is not None:
            self.ui.filename_lnedt.setText(fname)

    def getfile(self):
        fname = self.ui.filename_lnedt.text()
        if self.ui.new_radio.isChecked():
            mode = 'w-'
        else:
            mode = 'a'
        return fname, mode