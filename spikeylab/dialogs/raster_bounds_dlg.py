from PyQt4 import QtGui
from rasterform import Ui_RasterBoundsDialog

class RasterBoundsDialog(QtGui.QDialog, Ui_RasterBoundsDialog):
    def __init__(self,  parent=None, bounds=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)

        if bounds is not None:
            self.lower_lnedt.setText(str(bounds[0]))
            self.upper_lnedt.setText(str(bounds[1]))

    def get_values(self):
        lower = float(self.lower_lnedt.text())
        upper = float(self.upper_lnedt.text())
        return (lower, upper)