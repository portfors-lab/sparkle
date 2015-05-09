import os

import test.sample as sample
from sparkle.QtWrapper.QtGui import QApplication
from sparkle.gui.main_control import MainWindow
from sparkle.gui.stim.abstract_editor import AbstractEditorWidget


class TestUnitChanges():

    def setUp(self):
        self.tempfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), u"tmp", 'testinputs.json')

    def tearDown(self):
        try:
            os.remove(self.tempfile)        
        except:
            print 'remove failed'
        sample.reset_input_file()

    def test_freq_khz(self):
        """Assumes default scale of khz"""
        control = MainWindow(self.tempfile)
        control.show()

        fs0 = 200000.0
        fs1 = 200.0
        # manually set the inputs of interest
        control.ui.exploreStimEditor.ui.aofsSpnbx.setValue(fs0)
        control.ui.aifsSpnbx.setValue(fs1)

        assert control.ui.exploreStimEditor.ui.aofsSpnbx.value() == fs0
        assert control.ui.aifsSpnbx.value() == fs1

        frequency_inputs = control.frequencyInputs + AbstractEditorWidget.funit_fields
        for field in frequency_inputs:
            field.decimals() == 3
            field.minimum() == 0.001

        control.updateUnitLabels(control.tscale, 'Hz')

        assert control.ui.exploreStimEditor.ui.aofsSpnbx.value() == fs0 
        assert control.ui.aifsSpnbx.value() == fs1
        for field in frequency_inputs:
            field.minimum() == 1

        control.close()

    def test_freq_hz(self):
        control = MainWindow(self.tempfile)
        control.show()

        fs0 = 200000.0
        fs1 = 200.0
        # manually set the inputs of interest
        control.ui.exploreStimEditor.ui.aofsSpnbx.setValue(fs0)
        control.ui.aifsSpnbx.setValue(fs1)

        assert control.ui.exploreStimEditor.ui.aofsSpnbx.value() == fs0
        assert control.ui.aifsSpnbx.value() == fs1

        control.updateUnitLabels(control.tscale, 's')
        control.updateUnitLabels(control.tscale, 'ms')

        print 'spin boxes', control.ui.aifsSpnbx.value(), fs1
        assert control.ui.exploreStimEditor.ui.aofsSpnbx.value() == fs0 
        assert control.ui.aifsSpnbx.value() == fs1

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
        control.ui.windowszSpnbx.setValue(t0)
        control.ui.binszSpnbx.setValue(t1)

        assert control.ui.windowszSpnbx.value() == t0
        assert control.ui.binszSpnbx.value() == t1

        assert_fields_ms(control)

        # change it back
        control.updateUnitLabels('s', control.fscale)

        assert control.ui.windowszSpnbx.value() == t0 
        assert control.ui.binszSpnbx.value() == t1

        assert_fields_s(control)

        control.close()

    def test_time_s(self):
        """Assumes default scale of ms"""
        control = MainWindow(self.tempfile)
        control.show()

        t0 = 3.0
        t1 = 0.003
        # manually set the inputs of interest
        control.ui.windowszSpnbx.setValue(t0)
        control.ui.binszSpnbx.setValue(t1)

        assert control.ui.windowszSpnbx.value() == t0
        assert control.ui.binszSpnbx.value() == t1

        control.updateUnitLabels('s', control.fscale)
        control.updateUnitLabels('ms', control.fscale)

        assert control.ui.windowszSpnbx.value() == t0
        assert control.ui.binszSpnbx.value() == t1
        
        assert_fields_ms(control)

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

        assert_fields_s(control)

        control.close()

    def test_default_inputs_hz(self):
        control = MainWindow(sample.hzsinputs())
        control.show()

        fs0 = 200000.0
        fs1 = 200.0
        # manually set the inputs of interest
        control.ui.exploreStimEditor.ui.aofsSpnbx.setValue(fs0)
        control.ui.aifsSpnbx.setValue(fs1)

        assert control.ui.exploreStimEditor.ui.aofsSpnbx.value() == fs0 
        assert control.ui.aifsSpnbx.value() == fs1

        frequency_inputs = control.frequencyInputs + AbstractEditorWidget.funit_fields
        for field in frequency_inputs:
            field.decimals() == 0
            field.minimum() == 1

        control.close()

def assert_fields_s(control):
    time_inputs = control.timeInputs + AbstractEditorWidget.tunit_fields
    for field in time_inputs:
        assert field.suffix() == ' s'
    # test some known min/maxes
    assert control.ui.windowszSpnbx.minimum() == 0.00
    assert control.ui.binszSpnbx.minimum() == 0.00
    assert control.ui.windowszSpnbx.maximum() == 3
    assert control.ui.binszSpnbx.maximum() == 3
    # most editors in parameter stack should have a risefall and duration
    # field -- although if any components overwrite the default this 
    # will fail
    for editor_widget in control.ui.exploreStimEditor.allComponentWidgets():
        if 'risefall' in editor_widget.inputWidgets:
            assert editor_widget.inputWidgets['risefall'].minimum() == 0
            assert editor_widget.inputWidgets['risefall'].maximum() == 0.1
            assert editor_widget.inputWidgets['risefall'].suffix() == ' s'
        if 'duration' in editor_widget.inputWidgets:
            assert editor_widget.inputWidgets['duration'].minimum() == 0
            assert editor_widget.inputWidgets['duration'].maximum() == 3
            print editor_widget.name(), editor_widget.inputWidgets['duration'].suffix()
            assert editor_widget.inputWidgets['duration'].suffix() == ' s'
    for component_stack in control.ui.exploreStimEditor.trackEditorWidgets():
        assert component_stack.delaySpnbx.suffix() == ' s'

def assert_fields_ms(control):
    time_inputs = control.timeInputs + AbstractEditorWidget.tunit_fields
    for field in time_inputs:
        assert field.suffix() == ' ms'
    # check max/mins
    assert control.ui.windowszSpnbx.minimum() == 0
    assert control.ui.binszSpnbx.minimum() == 0
    assert control.ui.windowszSpnbx.maximum() == 3
    assert control.ui.binszSpnbx.maximum() == 3
    for editor_widget in control.ui.exploreStimEditor.allComponentWidgets():
        if 'risefall' in editor_widget.inputWidgets:
            assert editor_widget.inputWidgets['risefall'].minimum() == 0
            assert editor_widget.inputWidgets['risefall'].maximum() == 0.1
            assert editor_widget.inputWidgets['risefall'].suffix() == ' ms'
        if 'duration' in editor_widget.inputWidgets:
            assert editor_widget.inputWidgets['duration'].minimum() == 0
            assert editor_widget.inputWidgets['duration'].maximum() == 3.0
            assert editor_widget.inputWidgets['duration'].suffix() == ' ms'
    for component_stack in control.ui.exploreStimEditor.trackEditorWidgets():
        assert component_stack.delaySpnbx.suffix() == ' ms'
