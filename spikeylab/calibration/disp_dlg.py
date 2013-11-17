from __future__ import division
from PyQt4 import QtGui
from dispform import Ui_DisplayDlg

class DisplayDialog(QtGui.QDialog):
    def __init__(self, parent=None, default_vals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_DisplayDlg()
        self.ui.setupUi(self)

        if default_vals is not None:
            self.ui.chunksz_lnedt.setText(unicode(default_vals[u'chunksz']))
            self.ui.caldb_lnedt.setText(unicode(default_vals[u'caldb']))
            self.ui.calV_lnedt.setText(unicode(default_vals[u'calv']))
            try:
                calf = int(default_vals[u'calf']/1000)
            except:
                calf = None
            self.ui.calkhz_lnedt.setText(unicode(calf))

    def get_values(self):
        try:
            chsz = int(self.ui.chunksz_lnedt.text())
            caldb = int(self.ui.caldb_lnedt.text())
            calv = float(self.ui.calV_lnedt.text())
            calf = int(self.ui.calkhz_lnedt.text())*1000
        except ValueError, ve:
            val = unicode(ve).split(u':')
            QtGui.QMessageBox.warning(self, u'Invalid input', u'Invalid entry '+val[1])

            return None,None,None,None

        return chsz, caldb, calv, calf
