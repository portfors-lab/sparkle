from PyQt4 import QtGui
from dispform import Ui_DisplayDlg

class DisplayDialog(QtGui.QDialog):
    def __init__(self, parent=None, default_vals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_DisplayDlg()
        self.ui.setupUi(self)

        if default_vals is not None:
            self.ui.chunksz_lnedt.setText(str(default_vals['chunksz']))

    def get_values(self):
        return int(self.ui.chunksz_lnedt.text())
