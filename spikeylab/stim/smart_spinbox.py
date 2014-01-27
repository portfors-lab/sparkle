from PyQt4 import QtGui

from numpy import floor

class SmartSpinBox(QtGui.QDoubleSpinBox):
    def textFromValue(self, val):
        if val - floor(val) > 0.0:
            return str(val)
        else:
            return str(int(val))