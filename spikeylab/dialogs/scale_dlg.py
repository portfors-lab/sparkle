from PyQt4 import QtGui
from scaleform import Ui_ScaleDlg

class ScaleDialog(QtGui.QDialog):
    def __init__(self,  parent=None, defaultVals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_ScaleDlg()
        self.ui.setupUi(self)

        if defaultVals is not None:
            if defaultVals[u'fscale'] == 1:
                self.ui.hzBtn.setChecked(True)
            elif defaultVals[u'fscale'] == 1000:
                self.ui.khzBtn.setChecked(True)
            else:
                raise Exception(u"Invalid frequency scale")

            if defaultVals[u'tscale'] == 1:
                self.ui.secBtn.setChecked(True)
            elif defaultVals[u'tscale'] == 0.001:
                self.ui.msBtn.setChecked(True)
            else:
                raise Exception(u"Invalid time scale")

    def values(self):

        if self.ui.hzBtn.isChecked():
            fscale = 1
        else:
            fscale = 1000

        if self.ui.msBtn.isChecked():
            tscale = 0.001
        else:
            tscale = 1

        return fscale, tscale
