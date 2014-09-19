from PyQt4 import QtGui
from rasterform import Ui_RasterBoundsDialog

class RasterBoundsDialog(QtGui.QDialog, Ui_RasterBoundsDialog):
    """Dialog for setting where the raster plot should appear in relation
    to the spike trace"""
    def __init__(self,  parent=None, bounds=None):
        QtGui.QDialog.__init__(self,parent)
        self.setupUi(self)

        if bounds is not None:
            self.lowerLnedt.setText(str(bounds[0]))
            self.upperLnedt.setText(str(bounds[1]))

    def values(self):
        """Gets the user enter max and min values of where the 
        raster points should appear on the y-axis

        :returns: (float, float) -- (min, max) y-values to bound the raster plot by
        """
        lower = float(self.lowerLnedt.text())
        upper = float(self.upperLnedt.text())
        return (lower, upper)