from PyQt4 import QtGui
from specgramform import Ui_SpecDialog
from enthought.chaco import default_colormaps

class SpecDialog(QtGui.QDialog):
    def __init__(self, parent=None, default_vals=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui = Ui_SpecDialog()
        self.ui.setupUi(self)

        colormaps = default_colormaps.color_map_name_dict.keys()
        self.ui.colormap_cmbx.addItems(colormaps)

        if default_vals is not None:
            self.ui.nfft_spnbx.setValue(default_vals[u'nfft'])
            funcs = [self.ui.window_cmbx.itemText(i).lower() for i in xrange(self.ui.window_cmbx.count())]
            func_index = funcs.index(default_vals[u'window'])
            self.ui.window_cmbx.setCurrentIndex(func_index)
            self.ui.overlap_spnbx.setValue(default_vals['overlap'])
            cmap_index = colormaps.index(default_vals[u'colormap'])
            self.ui.colormap_cmbx.setCurrentIndex(cmap_index)

    def values(self):
        nfft = self.ui.nfft_spnbx.value()
        window = self.ui.window_cmbx.currentText().lower()
        overlap = self.ui.overlap_spnbx.value()
        colormap = self.ui.colormap_cmbx.currentText()
        return {u'nfft':nfft, u'window':window, u'overlap':overlap, u'colormap':colormap}