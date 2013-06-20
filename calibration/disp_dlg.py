from PyQt4 import QtGui
from dispform import Ui_DisplayDlg

class DisplayDialog(QtGui.QDialog):
    def __init__(self, parent=None, default_vals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_DisplayDlg()
        self.ui.setupUi(self)

        if default_vals is not None:
            self.ui.chunksz_lnedt.setText(str(default_vals['chunksz']))
            self.ui.caldb_lnedt.setText(str(default_vals['caldb']))
            self.ui.calV_lnedt.setText(str(default_vals['calv']))
            try:
                calf = int(default_vals['calf']/1000)
            except:
                calf = None
            self.ui.calkhz_lnedt.setText(str(calf))

    def get_values(self):
        try:
            chsz = int(self.ui.chunksz_lnedt.text())
            caldb = int(self.ui.caldb_lnedt.text())
            calv = float(self.ui.calV_lnedt.text())
            calf = int(self.ui.calkhz_lnedt.text())*1000
        except ValueError as ve:
            val = str(ve).split(':')
            QtGui.QMessageBox.warning(self, 'Invalid input', 'Invalid entry '+val[1])

            return None,None,None,None

        return chsz, caldb, calv, calf
