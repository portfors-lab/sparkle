from PyQt4 import QtGui
from savingform import Ui_SaveOptDlg

class SavingDialog(QtGui.QDialog):
    def __init__(self, parent=None, default_vals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_SaveOptDlg()
        self.ui.setupUi(self)

        if default_vals is not None:
            self.ui.savefolder_lnedt.setText(default_vals['savefolder'])
            self.ui.savename_lnedt.setText(default_vals['savename'])
            formats = [self.ui.saveformat_cmbx.itemText(i) for i in range(self.ui.saveformat_cmbx.count())]
            formatidx = formats.index(default_vals['saveformat'])
            self.ui.saveformat_cmbx.setCurrentIndex(formatidx)

    def browse_folders(self):
        folder = QtGui.QFileDialog.getExistingDirectory(self, "select folder",  self.ui.savefolder_lnedt.text())
        self.ui.savefolder_lnedt.setText(folder)
        #bdlg.setFileMode(QtGui.QFileDialog.Directory)
        #bdlg.setOption(QtGui.QFileDialog.ShowDirsOnly)
        #bdlg.exec_()

    def get_values(self):
        folder = self.ui.savefolder_lnedt.text()
        name = self.ui.savename_lnedt.text()
        sformat = self.ui.saveformat_cmbx.currentText()

        return folder, name, sformat
