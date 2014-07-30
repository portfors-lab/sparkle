from PyQt4 import QtGui
from rasterform import Ui_RasterBoundsDialog

class RasterBoundsDialog(QtGui.QDialog, Ui_RasterBoundsDialog):
    def __init__(self,  parent=None, bounds=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)

        if bounds is not None:
            self.lowerLnedt.setText(str(bounds[0]))
            self.upperLnedt.setText(str(bounds[1]))

    def values(self):
        lower = float(self.lowerLnedt.text())
        upper = float(self.upperLnedt.text())
        return (lower, upper)