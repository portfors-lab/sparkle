from PyQt4 import QtGui
from scaleform import Ui_ScaleDlg

class ScaleDialog(QtGui.QDialog):
    def __init__(self,  parent=None, default_vals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_ScaleDlg()
        self.ui.setupUi(self)

        if default_vals is not None:
            if default_vals[u'fscale'] == 1:
                self.ui.hz_btn.setChecked(True)
            elif default_vals[u'fscale'] == 1000:
                self.ui.khz_btn.setChecked(True)
            else:
                raise Exception(u"Invalid frequency scale")

            if default_vals[u'tscale'] == 1:
                self.ui.sec_btn.setChecked(True)
            elif default_vals[u'tscale'] == 0.001:
                self.ui.ms_btn.setChecked(True)
            else:
                raise Exception(u"Invalid time scale")

    def get_values(self):

        if self.ui.hz_btn.isChecked():
            fscale = 1
        else:
            fscale = 1000

        if self.ui.ms_btn.isChecked():
            tscale = 0.001
        else:
            tscale = 1

        return fscale, tscale
