from spikeylab.gui.stim.smart_spinbox import SmartSpinBox

def test_no_scale():
    box = SmartSpinBox()
    val = 4
    box.setValue(val)
    assert box.value() == val
    assert box.text() == str(val)

def test_ms_before_set():
    box = SmartSpinBox()
    box.setScale(SmartSpinBox.MilliSeconds)
    val = 0.004
    box.setValue(val)
    print 'val', box.value(), 'text', box.text()
    assert box.value() == val
    assert box.text() == '4 ms'

def test_ms_after_set():
    box = SmartSpinBox()
    val = 0.004
    box.setValue(val)
    box.setScale(SmartSpinBox.MilliSeconds)
    assert box.value() == val
    assert box.text() == '4 ms'

def test_s_before_set():
    box = SmartSpinBox()
    box.setScale(SmartSpinBox.Seconds)
    val = 0.004
    box.setValue(val)
    assert box.value() == val
    assert box.text() == '0.004 s'

def test_s_after_set():
    box = SmartSpinBox()
    val = 0.004
    box.setValue(val)
    box.setScale(SmartSpinBox.Seconds)
    assert box.value() == val
    assert box.text() == '0.004 s'

def test_ms_to_s():
    box = SmartSpinBox()
    val = 0.004
    box.setValue(val)
    box.setScale(SmartSpinBox.MilliSeconds)
    assert box.value() == val
    box.setScale(SmartSpinBox.Seconds)
    assert box.value() == val
    assert box.text() == '0.004 s'

def test_khz_before_set():
    box = SmartSpinBox()
    val = 6000
    box.setScale(SmartSpinBox.kHz)
    box.setValue(val)
    print box.value()
    assert box.value() == val
    print box.text()
    assert box.text() == '6 kHz'

def test_khz_before_set():
    box = SmartSpinBox()
    val = 6000
    box.setValue(val)
    box.setScale(SmartSpinBox.kHz)
    assert box.value() == val
    assert box.text() == '6 kHz'

def test_khz_before_set_small():
    box = SmartSpinBox()
    val = 6
    box.setScale(SmartSpinBox.kHz)
    box.setValue(val)
    assert box.value() == val
    assert box.text() == '0.006 kHz'

def test_khz_after_set_small():
    box = SmartSpinBox()
    val = 6
    box.setValue(val)
    box.setScale(SmartSpinBox.kHz)
    assert box.value() == val
    assert box.text() == '0.006 kHz'

def test_hz():
    box = SmartSpinBox()
    box.setScale(SmartSpinBox.Hz)
    val = 6
    box.setValue(val)
    assert box.value() == val
    assert box.text() == '6 Hz'