from sparkle.gui.plotting.raster_bounds_dlg import RasterBoundsDialog


class TestRasterDialog():
    def test_dlg(self):
        dlg = RasterBoundsDialog(bounds=(0.1, 0.33))
        assert dlg.values() == (0.1, 0.33)
