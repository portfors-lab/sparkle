from PyQt4 import QtGui
from specgramform import Ui_SpecDialog
from matplotlib import cm

class SpecDialog(QtGui.QDialog):
    def __init__(self, parent=None, default_vals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_SpecDialog()
        self.ui.setupUi(self)

        if default_vals is not None:
            self.ui.nfft_spnbx.setValue(default_vals[u'nfft'])
            funcs = [self.ui.window_cmbx.itemText(i).lower() for i in xrange(self.ui.window_cmbx.count())]
            func_index = funcs.index(default_vals[u'window'])
            self.ui.window_cmbx.setCurrentIndex(func_index)
            self.ui.overlap_spnbx.setValue(default_vals['overlap'])

        self.vals = default_vals

    def values(self):
        self.vals['nfft'] = self.ui.nfft_spnbx.value()
        self.vals['window'] = self.ui.window_cmbx.currentText().lower()
        self.vals['overlap'] = self.ui.overlap_spnbx.value()
        return self.vals