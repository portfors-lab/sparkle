import os

from spikeylab.gui.control import MainWindow

from PyQt4.QtGui import QApplication

app = None
def setUp():
    global app
    app = QApplication([])

def tearDown():
    global app
    app.exit(0)

class TestUnitChanges():

    def setUp(self):
        self.tempfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp", 'testinputs.json')

    def tearDown(self):
        try:
            os.remove(self.tempfile)        
        except:
            print 'remove failed'

    def test_freq_khz(self):
        """Assumes default scale of khz"""
        control = MainWindow(self.tempfile)
        control.show()

        fs0 = 200000.0
        fs1 = 200.0
        # manually set the inputs of interest
        control.ui.aosrSpnbx.setValue(fs0/1000)
        control.ui.aisrSpnbx.setValue(fs1/1000)

        assert control.ui.aosrSpnbx.value() == fs0/1000 
        assert control.ui.aisrSpnbx.value() == fs1/1000

        control.updateUnitLabels(control.tscale, 1)

        assert control.ui.aosrSpnbx.value() == fs0 
        assert control.ui.aisrSpnbx.value() == fs1

        control.close()

    def test_freq_hz(self):
        control = MainWindow(self.tempfile)
        control.show()

        fs0 = 200000.0
        fs1 = 200.0
        # manually set the inputs of interest
        control.ui.aosrSpnbx.setValue(fs0/1000)
        control.ui.aisrSpnbx.setValue(fs1/1000)

        assert control.ui.aosrSpnbx.value() == fs0/1000 
        assert control.ui.aisrSpnbx.value() == fs1/1000

        control.updateUnitLabels(control.tscale, 1)
        control.updateUnitLabels(control.tscale, 1000)

        print 'spin boxes', control.ui.aisrSpnbx.value(), fs1/1000
        assert control.ui.aosrSpnbx.value() == fs0/1000 
        assert control.ui.aisrSpnbx.value() == fs1/1000

        control.close()

    def test_time_ms(self):
        """Assumes default scale of ms"""
        control = MainWindow(self.tempfile)
        control.show()

        t0 = 3.0
        t1 = 0.003
        # manually set the inputs of interest
        control.ui.windowszSpnbx.setValue(t0/0.001)
        control.ui.binszSpnbx.setValue(t1/0.001)

        assert control.ui.windowszSpnbx.value() == t0/0.001
        assert control.ui.binszSpnbx.value() == t1/0.001

        control.updateUnitLabels(1, control.fscale)

        assert control.ui.windowszSpnbx.value() == t0 
        assert control.ui.binszSpnbx.value() == t1

        control.close()

    def test_time_s(self):
        """Assumes default scale of ms"""
        control = MainWindow(self.tempfile)
        control.show()

        t0 = 3.0
        t1 = 0.003
        # manually set the inputs of interest
        control.ui.windowszSpnbx.setValue(t0/0.001)
        control.ui.binszSpnbx.setValue(t1/0.001)

        assert control.ui.windowszSpnbx.value() == t0/0.001
        assert control.ui.binszSpnbx.value() == t1/0.001

        control.updateUnitLabels(1, control.fscale)
        control.updateUnitLabels(0.001, control.fscale)

        assert control.ui.windowszSpnbx.value() == t0/0.001
        assert control.ui.binszSpnbx.value() == t1/0.001

        control.close()