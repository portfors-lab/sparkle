from PyQt4 import QtGui
from scaleform import Ui_ScaleDlg

class ScaleDialog(QtGui.QDialog):
    def __init__(self,  parent=None, default_vals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_ScaleDlg()
        self.ui.setupUi(self)


        if default_vals is not None:
            self.ui.fscale_spnbx.setValue(default_vals['fscale'])
            self.ui.tscale_spnbx.setValue(default_vals['tscale'])

    def get_values(self):
        fscale = self.ui.fscale_spnbx.value()
        tscale = self.ui.tscale_spnbx.value()
        return fscale, tscale
