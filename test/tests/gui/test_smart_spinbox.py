from sparkle.gui.stim.smart_spinbox import SmartSpinBox


class TestSmartSpinBox():
    def setUp(self):
        self.box = SmartSpinBox()
        self.box.setMaximum(10000)
        self.box.setDecimals(3)

    def test_no_scale(self):
        val = 4
        self.box.setValue(val)
        assert self.box.value() == val
        assert self.box.text() == str(val)

    def test_ms_before_set(self):
        self.box.setScale(SmartSpinBox.MilliSeconds)
        val = 0.004
        self.box.setValue(val)
        print 'val', self.box.value(), 'text', self.box.text()
        assert self.box.value() == val
        assert self.box.text() == '4 ms'

    def test_ms_after_set(self):
        val = 0.004
        self.box.setValue(val)
        self.box.setScale(SmartSpinBox.MilliSeconds)
        assert self.box.value() == val
        assert self.box.text() == '4 ms'

    def test_s_before_set(self):
        self.box.setScale(SmartSpinBox.Seconds)
        val = 0.004
        self.box.setValue(val)
        assert self.box.value() == val
        assert self.box.text() == '0.004 s'

    def test_s_after_set(self):
        val = 0.004
        self.box.setValue(val)
        self.box.setScale(SmartSpinBox.Seconds)
        assert self.box.value() == val
        assert self.box.text() == '0.004 s'

    def test_ms_to_s(self):
        val = 0.004
        self.box.setValue(val)
        self.box.setScale(SmartSpinBox.MilliSeconds)
        assert self.box.value() == val
        self.box.setScale(SmartSpinBox.Seconds)
        assert self.box.value() == val
        assert self.box.text() == '0.004 s'

    def test_khz_before_set(self):
        val = 6000
        self.box.setScale(SmartSpinBox.kHz)
        self.box.setValue(val)
        print self.box.value()
        assert self.box.value() == val
        print self.box.text()
        assert self.box.text() == '6 kHz'

    def test_khz_before_set(self):
        val = 6000
        self.box.setValue(val)
        self.box.setScale(SmartSpinBox.kHz)
        print self.box.value(), val
        assert self.box.value() == val
        assert self.box.text() == '6 kHz'

    def test_khz_before_set_small(self):
        val = 6
        self.box.setScale(SmartSpinBox.kHz)
        self.box.setValue(val)
        assert self.box.value() == val
        assert self.box.text() == '0.006 kHz'

    def test_khz_after_set_small(self):
        val = 6
        self.box.setValue(val)
        self.box.setScale(SmartSpinBox.kHz)
        assert self.box.value() == val
        assert self.box.text() == '0.006 kHz'

    def test_hz(self):
        self.box.setScale(SmartSpinBox.Hz)
        val = 6
        self.box.setValue(val)
        assert self.box.value() == val
        assert self.box.text() == '6 Hz'

    def test_mVV(self):
        self.box.setScalarFactor('mV/V', 20)
        self.box.setScale(SmartSpinBox.mVV)
        val = 1
        self.box.setValue(val)
        assert self.box.value() == val
        assert self.box.text() == '20 mV'
        self.box.setScalarFactor('mV/V', 1000)
        assert self.box.value() == val
        assert self.box.text() == '1000 mV'

    def test_pAV(self):
        self.box.setScalarFactor('pA/V', 400)
        self.box.setScale(SmartSpinBox.pAV)
        val = 1
        self.box.setValue(val)
        assert self.box.value() == 1
        assert self.box.text() == '400 pA'
        self.box.setScalarFactor('pA/V', 1000)
        assert self.box.value() == 1
        assert self.box.text() == '1000 pA'
