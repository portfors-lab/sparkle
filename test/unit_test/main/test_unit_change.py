import os

from spikeylab.main.control import MainWindow

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
        control.ui.aosr_spnbx.setValue(fs0/1000)
        control.ui.aisr_spnbx.setValue(fs1/1000)

        assert control.ui.aosr_spnbx.value() == fs0/1000 
        assert control.ui.aisr_spnbx.value() == fs1/1000

        control.update_unit_labels(control.tscale, 1)

        assert control.ui.aosr_spnbx.value() == fs0 
        assert control.ui.aisr_spnbx.value() == fs1

        control.close()

    def test_freq_hz(self):
        control = MainWindow(self.tempfile)
        control.show()

        fs0 = 200000.0
        fs1 = 200.0
        # manually set the inputs of interest
        control.ui.aosr_spnbx.setValue(fs0/1000)
        control.ui.aisr_spnbx.setValue(fs1/1000)

        assert control.ui.aosr_spnbx.value() == fs0/1000 
        assert control.ui.aisr_spnbx.value() == fs1/1000

        control.update_unit_labels(control.tscale, 1)
        control.update_unit_labels(control.tscale, 1000)

        print 'spin boxes', control.ui.aisr_spnbx.value(), fs1/1000
        assert control.ui.aosr_spnbx.value() == fs0/1000 
        assert control.ui.aisr_spnbx.value() == fs1/1000

        control.close()

    def test_time_ms(self):
        """Assumes default scale of ms"""
        control = MainWindow(self.tempfile)
        control.show()

        t0 = 3.0
        t1 = 0.003
        # manually set the inputs of interest
        control.ui.windowsz_spnbx.setValue(t0/0.001)
        control.ui.binsz_spnbx.setValue(t1/0.001)

        assert control.ui.windowsz_spnbx.value() == t0/0.001
        assert control.ui.binsz_spnbx.value() == t1/0.001

        control.update_unit_labels(1, control.fscale)

        assert control.ui.windowsz_spnbx.value() == t0 
        assert control.ui.binsz_spnbx.value() == t1

        control.close()

    def test_time_s(self):
        """Assumes default scale of ms"""
        control = MainWindow(self.tempfile)
        control.show()

        t0 = 3.0
        t1 = 0.003
        # manually set the inputs of interest
        control.ui.windowsz_spnbx.setValue(t0/0.001)
        control.ui.binsz_spnbx.setValue(t1/0.001)

        assert control.ui.windowsz_spnbx.value() == t0/0.001
        assert control.ui.binsz_spnbx.value() == t1/0.001

        control.update_unit_labels(1, control.fscale)
        control.update_unit_labels(0.001, control.fscale)

        assert control.ui.windowsz_spnbx.value() == t0/0.001
        assert control.ui.binsz_spnbx.value() == t1/0.001

        control.close()