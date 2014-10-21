import os

from QtWrapper.QtGui import QApplication

from spikeylab.gui.main_control import MainWindow
from spikeylab.gui.stim.abstract_editor import AbstractEditorWidget

import test.sample as sample

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

        frequency_inputs = control.frequencyInputs + AbstractEditorWidget.funit_fields
        for field in frequency_inputs:
            field.decimals() == 3
            field.minimum() == 0.001

        control.updateUnitLabels(control.tscale, 1)

        assert control.ui.aosrSpnbx.value() == fs0 
        assert control.ui.aisrSpnbx.value() == fs1
        for field in frequency_inputs:
            field.decimals() == 0
            field.minimum() == 1

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

        frequency_inputs = control.frequencyInputs + AbstractEditorWidget.funit_fields
        for field in frequency_inputs:
            field.decimals() == 3
            field.minimum() == 0.001

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

        time_inputs = control.timeInputs + AbstractEditorWidget.tunit_fields
        for field in time_inputs:
            assert field.decimals() == 0
            assert field.minimum() == 1

        control.updateUnitLabels(1, control.fscale)

        assert control.ui.windowszSpnbx.value() == t0 
        assert control.ui.binszSpnbx.value() == t1

        for field in time_inputs:
            assert field.decimals() == 3
            assert field.minimum() == 0.001

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
        
        time_inputs = control.timeInputs + AbstractEditorWidget.tunit_fields
        for field in time_inputs:
            assert field.decimals() == 0
            assert field.minimum() == 1

        control.close()

    def test_default_inputs_s(self):
        control = MainWindow(sample.hzsinputs())
        control.show()

        t0 = 3.0
        t1 = 0.003
        # manually set the inputs of interest
        control.ui.windowszSpnbx.setValue(t0)
        control.ui.binszSpnbx.setValue(t1)

        assert control.ui.windowszSpnbx.value() == t0
        assert control.ui.binszSpnbx.value() == t1

        time_inputs = control.timeInputs + AbstractEditorWidget.tunit_fields
        for field in time_inputs:
            assert field.decimals() == 3
            assert field.minimum() == 0.001

        control.close()

    def test_default_inputs_hz(self):
        control = MainWindow(sample.hzsinputs())
        control.show()

        fs0 = 200000.0
        fs1 = 200.0
        # manually set the inputs of interest
        control.ui.aosrSpnbx.setValue(fs0)
        control.ui.aisrSpnbx.setValue(fs1)

        assert control.ui.aosrSpnbx.value() == fs0 
        assert control.ui.aisrSpnbx.value() == fs1

        frequency_inputs = control.frequencyInputs + AbstractEditorWidget.funit_fields
        for field in frequency_inputs:
            field.decimals() == 0
            field.minimum() == 1

        control.close()
            