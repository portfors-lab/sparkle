from spikeylab.plotting.raster_bounds_dlg import RasterBoundsDialog

from PyQt4 import QtGui

class TestRasterDialog():
    def test_dlg(self):
        app = QtGui.QApplication([])
        dlg = RasterBoundsDialog(bounds=(0.1, 0.33))
        assert dlg.values() == (0.1, 0.33)
        del app