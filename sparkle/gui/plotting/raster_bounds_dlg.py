from sparkle.QtWrapper import QtGui
from raster_bounds_dlg_form import Ui_RasterBoundsDialog


class RasterBoundsDialog(QtGui.QDialog, Ui_RasterBoundsDialog):
    """Dialog for setting where the raster plot should appear in relation
    to the spike trace"""
    def __init__(self,  parent=None, bounds=None):
        super(RasterBoundsDialog, self).__init__(parent)
        self.setupUi(self)

        if bounds is not None:
            self.lowerSpnbx.setValue(bounds[0])
            self.upperSpnbx.setValue(bounds[1])

    def values(self):
        """Gets the user enter max and min values of where the 
        raster points should appear on the y-axis

        :returns: (float, float) -- (min, max) y-values to bound the raster plot by
        """
        lower = float(self.lowerSpnbx.value())
        upper = float(self.upperSpnbx.value())
        return (lower, upper)
