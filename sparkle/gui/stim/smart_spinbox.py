import re

from numpy import floor

from sparkle.QtWrapper import QtCore, QtGui


class SmartSpinBox(QtGui.QDoubleSpinBox):
    # enums
    MilliSeconds = 'ms'
    Seconds = 's'
    Hz = 'Hz'
    kHz = 'kHz'
    mVV = 'mV/V'
    pAV = 'pA/V'
    _factors = { mVV: 1./20, pAV: 1./400}
    """Spin box that shows decimals only if value is not a whole number"""
    def __init__(self, parent=None):
        super(SmartSpinBox, self).__init__(parent)
        # this will cause valueChanged signal to emit only then
        # editing is finished
        self.setKeyboardTracking(False)
        self._scalar = 1
        self.setDecimals(3)

    def textFromValue(self, val):
        val = val/self._scalar
        return trim(val)

    def setScale(self, scale):
        if scale == self.MilliSeconds:
            self._scalar = 0.001
            self.setDecimals(3)
        elif scale == self.Seconds:
            self._scalar = 1
            self.setDecimals(3)
        elif scale == self.Hz:
            self._scalar = 1
            self.setDecimals(3)
        elif scale == self.kHz:
            self._scalar = 1000.
            self.setDecimals(3)
        elif scale == self.mVV:
            self._scalar = self._factors[self.mVV]
            scale = 'mV'
        elif scale == self.pAV:
            self._scalar = self._factors[self.pAV]
            scale = 'pA'
        else:
            self._scalar = 1
            self.setDecimals(3)
        self.setSuffix(' '+scale)

    def valueFromText(self, text):
        numstr = re.match('-?\d*\.?\d*', text).group(0)
        if len(numstr) > 0 and numstr != '-':
            val = float(numstr)
        else:
            val = 0.
        return val*self._scalar

    def validate(self, inpt, pos):
        val = self.valueFromText(inpt)    
        if val <= self.maximum() and val >= self.minimum():
            return (2, pos)
        else:
            return (1, pos)

    def stepBy(self, steps):
        self.setValue(self.value() + (steps*self._scalar))

    def currentScale(self):
        return self._scalar

    def setScalarFactor(self, unit, factor):
        self._factors[str(unit)] = 1./factor
        self.setScale(unit)

    def scalarFactor(self, unit):
        return 1./self._factors[str(unit)]


def trim(val):
    if val - floor(val) > 0.0:
        return str(val)
    else:
        return str(int(val))
